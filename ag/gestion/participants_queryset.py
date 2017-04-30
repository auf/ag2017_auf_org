# -*- encoding: utf-8 -*-
from ag.gestion import consts
from ag.gestion.consts import *
from django.db.models.query import QuerySet

CASE_REGION_VOTE = "\n".join(["WHEN '{}' THEN '{}'".format(reg, reg_vote)
                              for reg, reg_vote
                              in REGION_AUF_REGION_VOTANTS.items()])

EXCEPT_DOM_TOM_SQL = "reference_etablissement.id in ({0})". \
    format(', '.join(map(str, EXCEPTIONS_DOM_TOM)))
CONDITION_VOTE_SQL = """
                    reference_etablissement.statut in ('T', 'A')
                    AND gestion_typeinstitution.code = '{TYPE_ETAB}'
                    AND gestion_participant.desactive = 0
                    AND reference_etablissement.qualite in ('RES', 'CIR', 'ESR')
                    """.format(TYPE_ETAB=consts.TYPE_INST_ETABLISSEMENT)
CALCUL_REGION_VOTE_SQL = """
                          IF({EXCEPT_DOM_TOM}, '{REG_EUROPE_OUEST}',
                             (CASE reference_region.code
                             {CASE_REGION_VOTE}
                             END)
                             )
        """.format(EXCEPT_DOM_TOM=EXCEPT_DOM_TOM_SQL,
                   CASE_REGION_VOTE=CASE_REGION_VOTE,
                   **REGIONS_VOTANTS_CONSTS_DICT)
REGION_VOTE_SQL = """
            IF({CONDITION_VOTE_SQL},
               {CALCUL_REGION_VOTE_SQL},
            NULL)""".format(CONDITION_VOTE_SQL=CONDITION_VOTE_SQL,
                            CALCUL_REGION_VOTE_SQL=CALCUL_REGION_VOTE_SQL)


SOMME_PAIEMENTS_GESTION = """SELECT coalesce(SUM(montant_euros), 0)
                      FROM gestion_paiement
                      WHERE participant_id=gestion_participant.id"""

SOMME_PAIEMENTS_PAYPAL = """SELECT coalesce(sum(montant), 0) FROM
                      (SELECT coalesce(min(montant), 0) as montant,
                      min(inscription_id) AS iid
                      FROM inscription_paypalresponse
                      WHERE validated=1
                      GROUP BY invoice_uid) AS montants
                      where iid = gestion_participant.inscription_id"""

SOMME_FORFAITS_CATEGORIE = """
  SELECT coalesce(sum(coalesce(montant, 0)), 0) FROM
  inscription_forfait WHERE categorie = '{CATEGORIE}'
  AND id in (
  SELECT forfait_id FROM gestion_participant_forfaits
  WHERE participant_id = gestion_participant.id)
"""


def somme_forfaits_categorie(categorie):
    return "({})".format(SOMME_FORFAITS_CATEGORIE.format(CATEGORIE=categorie))


class ParticipantsQuerySet(QuerySet):
    def actifs(self):
        return self.exclude(desactive=True)

    def represente_etablissement(self):
        return self.actifs().filter(fonction__type_institution__code=
                                    consts.TYPE_INST_ETABLISSEMENT)

    def represente_autre_institution(self):
        return self.exclude(fonction__type_institution__code=
                            consts.TYPE_INST_ETABLISSEMENT)

    def sql_expr(self, name):
        if name == 'hotel_manquant':
            return """(
                gestion_participant.hotel_id IS NULL
                AND gestion_participant.reservation_hotel_par_auf IS NOT NULL
                AND gestion_participant.reservation_hotel_par_auf = TRUE
            )"""
        elif name == 'reservation_hotel_manquante':
            return """(
                    gestion_participant.reservation_hotel_par_auf = 0
                    AND gestion_participant.prise_en_charge_sejour IS NOT NULL
                    AND gestion_participant.prise_en_charge_sejour = TRUE
                )"""
        elif name == 'trajet_manquant':
            return """(
                gestion_participant.vol_groupe_id is NULL
                AND NOT EXISTS(SELECT 1 FROM gestion_infosvol i
                    WHERE i.participant_id = gestion_participant.id
                        AND i.type_infos = '%s')
                AND gestion_participant.transport_organise_par_auf IS NOT NULL
                AND gestion_participant.transport_organise_par_auf = TRUE
                )""" % VOL_ORGANISE
        elif name == 'transport_non_organise':
            return """(
                gestion_participant.transport_organise_par_auf = FALSE
                AND gestion_participant.prise_en_charge_transport IS NOT NULL
                AND gestion_participant.prise_en_charge_transport = TRUE
                )"""
        elif name == 'prise_en_charge_a_completer':
            return """(
                gestion_participant.prise_en_charge_transport IS NULL
                OR gestion_participant.prise_en_charge_sejour IS NULL
            )"""
        elif name == 'nb_places_incorrect':
            return """(
                gestion_participant.hotel_id IS NOT NULL
                AND gestion_participant.reservation_hotel_par_auf IS NOT NULL
                AND gestion_participant.reservation_hotel_par_auf = TRUE
                AND IFNULL((
                    SELECT SUM(r.nombre * c.places)
                    FROM gestion_reservationchambre r, gestion_chambre c
                    WHERE
                        r.participant_id = gestion_participant.id
                        AND c.hotel_id = gestion_participant.hotel_id
                        AND c.type_chambre = r.type_chambre
                ), 0) !=
                (
                    SELECT COUNT(*)
                    FROM gestion_invite i
                    WHERE i.participant_id = gestion_participant.id
                ) + 1
            )"""
        elif name == 'delinquant':
            return """(
                gestion_participant.etablissement_id IN (
                    SELECT id FROM core_etablissementdelinquant
                )
            )"""
        elif name == 'problematique':
            return '(%s)' % ' OR '.join(
                self.sql_expr(probleme['sql_expr'])
                for probleme in PROBLEMES.values()
            )
        elif name == 'nombre_invites':
            return """(
                SELECT COUNT(*)
                FROM gestion_invite
                WHERE participant_id = gestion_participant.id
            )"""
        elif name == 'frais_inscription':
            return somme_forfaits_categorie(consts.CODE_CAT_INSCRIPTION)
        elif name == 'frais_inscription_facture':
            return """(IF(gestion_participant.prise_en_charge_inscription, 0,
            {}))""".format(self.sql_expr('frais_inscription'))
        elif name == 'frais_transport':
            return """IF(gestion_participant.transport_organise_par_auf=1,
                IFNULL( (
                SELECT SUM(COALESCE(prix,0))
                FROM gestion_infosvol
                WHERE
                    participant_id = gestion_participant.id
                    AND type_infos = %s
            ),0) + (IF(gestion_participant.vol_groupe_id IS NOT NULL,
                (SELECT SUM(COALESCE(prix,0))
                FROM gestion_infosvol
                WHERE
                    type_infos = %s
                    AND vol_groupe_id = gestion_participant.vol_groupe_id), 0)
            ),0)""" % (VOL_ORGANISE, VOL_GROUPE)
        elif name == 'frais_transport_facture':
            return """
                IF(gestion_participant.prise_en_charge_transport, 0, %s)
            """ % self.sql_expr('frais_transport')
        elif name == 'frais_hebergement':
            return """(IF(gestion_participant.reservation_hotel_par_auf,
                IFNULL((
                SELECT SUM(r.nombre * c.prix *
                            DATEDIFF(gestion_participant.date_depart_hotel,
                                    gestion_participant.date_arrivee_hotel))
                FROM gestion_reservationchambre r, gestion_chambre c
                WHERE
                    r.participant_id = gestion_participant.id
                    AND c.hotel_id = gestion_participant.hotel_id
                    AND c.type_chambre = r.type_chambre
                ), 0)
            ,0))"""
        elif name == 'frais_hebergement_facture':
            return """(
            IF(
                gestion_participant.prise_en_charge_sejour,
                {},
                {}
            )
            )""".format(
                somme_forfaits_categorie(consts.CODE_CAT_HEBERGEMENT),
                self.sql_expr('frais_hebergement'),
            )
        elif name == 'forfaits_invites':
            return "({} * {})".format(
                somme_forfaits_categorie(consts.CODE_CAT_INVITE),
                self.sql_expr('nombre_invites'))
        elif name == 'frais_autres':
            return """IFNULL((
                SELECT SUM(quantite * IFNULL(montant,0))
                FROM gestion_frais
                WHERE participant_id = gestion_participant.id
            ), 0)"""
        elif name == 'total_frais':
            return "(%s + %s + %s + %s + %s)" % (
                self.sql_expr('frais_inscription'),
                self.sql_expr('frais_transport'),
                self.sql_expr('frais_hebergement'),
                self.sql_expr('forfaits_invites'),
                self.sql_expr('frais_autres'),
            )
        elif name == 'total_facture':
            return "(%s + %s + %s + %s)" % (
                self.sql_expr('frais_inscription_facture'),
                self.sql_expr('frais_transport_facture'),
                self.sql_expr('frais_hebergement_facture'),
                self.sql_expr('forfaits_invites'),
            )
        elif name == 'solde':
            return "({} - ({}) - ({}))".format(
                self.sql_expr('total_facture'),
                SOMME_PAIEMENTS_GESTION,
                SOMME_PAIEMENTS_PAYPAL)
        elif name == 'solde_a_payer':
            return "(%s > 0)" % self.sql_expr('solde')
        elif name == 'aucun_solde_a_payer':
            return "(%s = 0)" % self.sql_expr('solde')
        elif name == 'paiement_en_trop':
            return "(%s < 0)" % self.sql_expr('solde')
        elif name == 'total_deja_paye_sql':
            return "(({}) + ({}))".format(SOMME_PAIEMENTS_GESTION,
                                          SOMME_PAIEMENTS_PAYPAL)
        else:
            raise ValueError('Expression inconnue: %s' % name)

    def sql_extra_fields(self, *fields):
        return self.extra(select=dict(
            (f, self.sql_expr(f)) for f in fields
        ))

    def sql_filter(self, template, *fields):
        return self.extra(where=([
            template % tuple(self.sql_expr(f) for f in fields)
        ]))

    def filter_representants_mandates(self):
        return self.filter(inscription__invitation__pour_mandate=True)

    def avec_problemes(self, *problemes_codes):
        qs = self
        for probleme_code in problemes_codes:
            probleme = consts.PROBLEMES[probleme_code]
            sql_expr_code = probleme['sql_expr']
            qs = qs.extra(select={
                sql_expr_code: self.sql_expr(sql_expr_code)})
        return qs

    def avec_region_vote(self):
        """
        Attention: petite assymétrie avec filter_region_vote: les
        votants français ont pour région "Europe de l'Ouest"
        """
        qs = self.extra(
            select={
                'region_vote': REGION_VOTE_SQL
            })
        return qs.select_related('etablissement', 'etablissement__region',
                                 'etablissement__pays',
                                 'fonction__type_institution',
                                 'implantation__region',
                                 'institution__region', )

    def count_par_region_vote(self, code_region_vote):
        return self.filter_representants_mandates() \
            .filter_region_vote(code_region_vote) \
            .filter(etablissement__region__nom__startswith='') \
            .count()

    def filter_region_vote(self, code_region_vote):
        """ Voir commentaire avec_region_vote()
        """
        qs = self.select_related('etablissement', 'etablissement__region',
                                 'fonction')

        # Lors d'un count, django ne tient pas compte du select_related
        # ce qui fait échouer notre requête qui s'attend à ce que
        # certaines tables soient présentes. Pour cette raison, on est
        # obligés de dupliquer les conditions de vote exprimées
        # dans CONDITION_VOTE_SQL
        return qs.extra(
            where=[
                "({0}) = '{1}'".format(CALCUL_REGION_VOTE_SQL, code_region_vote)
            ]
        )

    def filter_statut_etablissement(self, *codes_statuts):
        return self.filter(etablissement__statut__in=codes_statuts)

    def titulaires(self):
        return self.filter_statut_etablissement(consts.CODE_TITULAIRE)

    def candidats(self, code_election):
        return self.filter(candidat_a__code=code_election)\
            .prefetch_related('suppleant')

    def associes(self):
        return self.filter_statut_etablissement(consts.CODE_ASSOCIE)

    def filter_qualite_etablissement(self, *codes_qualites):
        return self.filter(etablissement__qualite__in=codes_qualites)

    def reseau(self):
        return self.filter_qualite_etablissement(consts.CODE_RESEAU)

    def elus(self):
        return self.filter(candidat_statut=ELU)

    def filter_votants(self):
        """ Voir commentaire avec_region_vote()
        """
        # la dernière condition force la jointure sur
        # region
        return self \
            .filter_statut_etablissement(consts.CODE_TITULAIRE,
                                         consts.CODE_ASSOCIE) \
            .actifs() \
            .filter_qualite_etablissement(consts.CODE_RESEAU,
                                          consts.CODE_CENTRE_RECHERCHE,
                                          consts.CODE_ETAB_ENSEIGNEMENT) \
            .filter_representants_mandates() \
            .avec_region_vote()\
            .filter(etablissement__region__nom__startswith='')
