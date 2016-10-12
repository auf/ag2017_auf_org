# -*- encoding: utf-8 -*-
from ag.gestion.consts import *
from ag.gestion.montants import get_infos_montants, infos_montant_par_code
from django.db.models import Q
from django.db.models.query import QuerySet

EXCEPT_DOM_TOM_SQL = "reference_etablissement.id in ({0})". \
    format(', '.join(map(str, EXCEPTIONS_DOM_TOM)))
CONDITION_VOTE_SQL = """
                    gestion_statutparticipant.droit_de_vote=1
                    AND reference_etablissement.statut in ('T', 'A')
                    AND gestion_participant.type_institution = 'E'
                    AND gestion_participant.desactive = 0
                    AND reference_etablissement.qualite in ('RES', 'CIR', 'ESR')
                    """
CALCUL_REGION_VOTE_SQL = """
        IF(reference_etablissement.qualite = 'RES', '{REG_RESEAU}',
                          IF({EXCEPT_DOM_TOM}, '{REG_EUROPE_OUEST}',
                             (CASE reference_region.code
                             WHEN 'ACGL' THEN '{REG_AFRIQUE}'
                             WHEN 'AO' THEN '{REG_AFRIQUE}'
                             WHEN 'A' THEN '{REG_AMERIQUES}'
                             WHEN 'C' THEN '{REG_AMERIQUES}'
                             WHEN 'AP' THEN '{REG_ASIE_PACIFIQUE}'
                             WHEN 'ECO' THEN '{REG_EUROPE_EST}'
                             WHEN 'EO' THEN '{REG_EUROPE_OUEST}'
                             WHEN 'M' THEN '{REG_MAGHREB}'
                             ELSE '{REG_MOYEN_ORIENT}'
                             END)
                             )
                       )
        """.format(EXCEPT_DOM_TOM=EXCEPT_DOM_TOM_SQL,
                   **REGIONS_VOTANTS_CONSTS_DICT)
REGION_VOTE_SQL = """
            IF({CONDITION_VOTE_SQL},
               {CALCUL_REGION_VOTE_SQL},
            NULL)""".format(CONDITION_VOTE_SQL=CONDITION_VOTE_SQL,
                            CALCUL_REGION_VOTE_SQL=CALCUL_REGION_VOTE_SQL)


class ParticipantsQuerySet(QuerySet):
    def actifs(self):
        return self.exclude(desactive=True)

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
            montants = get_infos_montants()
            return "(%s)" % (
                montants['frais_inscription'].montant,
            )
        elif name == 'frais_inscription_facture':
            montants = get_infos_montants()
            return """(
                %s - IF(gestion_participant.prise_en_charge_inscription, %s, 0)
            )""" % (
                self.sql_expr('frais_inscription'),
                montants['frais_inscription'].montant,
            )
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
                IF(
                    gestion_participant.facturation_supplement_chambre_double,
                    %s,
                    0
                ),
                %s
            )
            )""" % (
                infos_montant_par_code('supplement_chambre_double').montant,
                self.sql_expr('frais_hebergement'),
            )
        elif name == 'frais_activites':
            return """(
                SELECT IFNULL(
                    SUM(a.prix) +
                    SUM(IF(p.avec_invites, %s * a.prix_invite, 0)),
                    0
                )
                FROM gestion_participationactivite p
                    INNER JOIN gestion_activite a
                    ON a.id = p.activite_id
                WHERE
                    p.participant_id = gestion_participant.id
            )""" % self.sql_expr('nombre_invites')
        elif name == 'frais_activites_facture':
            return """(
                %s - IF(gestion_participant.prise_en_charge_activites, (
                    SELECT IFNULL(SUM(a.prix), 0)
                    FROM gestion_participationactivite p
                        INNER JOIN gestion_activite a
                        ON a.id = p.activite_id
                    WHERE
                        p.participant_id = gestion_participant.id
                ), 0)
            )""" % self.sql_expr('frais_activites')
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
                self.sql_expr('frais_activites'),
                self.sql_expr('frais_autres'),
            )
        elif name == 'total_facture':
            return "(%s + %s + %s + %s)" % (
                self.sql_expr('frais_inscription_facture'),
                self.sql_expr('frais_transport_facture'),
                self.sql_expr('frais_hebergement_facture'),
                self.sql_expr('frais_activites_facture'),
            )
        elif name == 'solde':
            return "(%s - gestion_participant.accompte)" % \
                   self.sql_expr('total_facture')
        elif name == 'solde_a_payer':
            return "(%s > 0)" % self.sql_expr('solde')
        elif name == 'paiement_en_trop':
            return "(%s < 0)" % self.sql_expr('solde')
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
                                 'statut', 'etablissement__pays')

    def filter_region_vote(self, code_region_vote):
        """ Voir commentaire avec_region_vote()
        """
        qs = self.select_related('etablissement', 'etablissement__region',
                                 'statut')
        # Lors d'un count, django ne tient pas compte du select_related
        # ce qui fait échouer notre requête qui s'attend à ce que
        # certaines tables soient présentes. Pour cette raison, on est
        # obligés de dupliquer les conditions de vote exprimées
        # dans CONDITION_VOTE_SQL
        qs = qs.filter_votants()
        qs = qs.filter(statut__droit_de_vote=True,
                       etablissement__statut__in=('T', 'A'),
                       type_institution='E',
                       desactive=False,
                       etablissement__qualite__in=('RES', 'CIR', 'ESR'),
                       # cette dernière condition force la jointure sur region
                       etablissement__region__nom__startswith='')
        if code_region_vote == REG_FRANCE:
            code_region_vote = REG_EUROPE_OUEST
            qs = qs.filter(Q(etablissement__pays__code='FR') |
                           Q(etablissement__id__in=EXCEPTIONS_DOM_TOM))
        return qs.extra(
            where=[
                "({0}) = '{1}'".format(CALCUL_REGION_VOTE_SQL, code_region_vote)
            ]
        )

    def filter_votants(self):
        """ Voir commentaire avec_region_vote()
        """
        return self.filter(statut__droit_de_vote=True,
                           etablissement__statut__in=('T', 'A'),
                           type_institution='E',
                           desactive=False,
                           etablissement__qualite__in=('RES', 'CIR', 'ESR'),
                           # cette dernière condition force la jointure sur
                           # region
                           etablissement__region__nom__startswith='')