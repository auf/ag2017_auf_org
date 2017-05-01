# -*- encoding: utf-8 -*-
from collections import namedtuple, defaultdict
from functools import partial
from itertools import groupby
import datetime

from ag.gestion import consts
from ag.gestion.consts import ARRIVEES, DEPARTS, VOL_ORGANISE, DEPART_SEULEMENT, ARRIVEE_SEULEMENT
from ag.gestion.models import (Participant, InfosVol, Invite, Activite, Hotel,
                               ParticipationActivite, ActiviteScientifique,
                               strip_accents, Frais, PointDeSuivi, Paiement)
from django.db import connection
from django.db.models import Q, Count, Prefetch
from django.utils.datastructures import SortedDict

from ag.inscription.models import get_forfaits, PaypalResponse

Element = namedtuple('DonneeEtat', ['titre', 'elements'])


def get_donnees_etat_participants():
    q_etablissements = Q(
        fonction__type_institution__code=consts.TYPE_INST_ETABLISSEMENT)
    q_observateur = Q(fonction__code=consts.CAT_FONCTION_OBSERVATEUR)
    q_instance_seulement = Q(fonction__code=consts.FONCTION_INSTANCE_SEULEMENT)
    q_personnel_auf = Q(fonction__code=consts.FONCTION_PERSONNEL_AUF)
    q_autres = (~q_etablissements & ~q_observateur & ~q_instance_seulement &
                ~q_personnel_auf)

    def get_participants_etablissements():
        participants = Participant.actifs\
            .filter(q_etablissements)\
            .select_related('etablissement', 'etablissement__pays',
                            'fonction')\
            .order_by('etablissement__pays__nom', 'etablissement__nom',
                      'fonction__ordre', 'nom', 'prenom')
        return recursive_group_by(
            list(participants),
            keys=[lambda p:p.etablissement.pays,
                  lambda p: p.etablissement,
                  lambda p:p.fonction],
            titles=[lambda p: p.nom, lambda e: e.nom, lambda s: s.libelle])

    def get_observateurs():
        participants = Participant.actifs \
            .filter(q_observateur) \
            .select_related('institution__region') \
            .order_by('institution__nom', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.nom_institution(), p.get_region())],
            titles=[lambda k: u"{0}, {1}".format(k[0], k[1].nom)])

    def get_instances():
        participants = Participant.actifs \
            .filter(q_instance_seulement)\
            .order_by('instance_auf', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.instance_auf, p.get_instance_auf_display())],
            titles=[lambda k: k[1]]
        )

    def get_personnel_auf():
        participants = Participant.actifs \
            .filter(q_personnel_auf) \
            .select_related('implantation__region')\
            .order_by('implantation__region__nom',
                      'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: p.get_region().nom],
            titles=[lambda k: k]
        )

    def get_autres():
        participants = Participant.actifs \
            .filter(q_autres)\
            .select_related('institution__region', 'implantation__region') \
            .order_by('institution__nom', 'institution__region__nom', 'nom',
                      'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.nom_institution(), p.get_region())],
            titles=[lambda k: u"{0}, {1}".format(k[0],
                                                 k[1].nom if k[1] else u"")])

    return (
        Element(u'Établissements', get_participants_etablissements()),
        Element(u'Observateurs', get_observateurs()),
        Element(u'Instances', get_instances()),
        Element(u'Personnel AUF', get_personnel_auf()),
        Element(u'Autre', get_autres()),
    )


def recursive_group_by(liste, keys, titles):
    result = []
    for groupe in groupby(liste, key=keys[0]):
        sous_liste = []
        result.append(Element(titles[0](groupe[0]), sous_liste))
        if len(keys) > 1:
            sous_liste.extend(recursive_group_by(groupe[1], keys[1:],
                                                 titles[1:]))
        else:
            sous_liste.extend(groupe[1])
    return result


def get_donnees_arrivees_departs(arrivees_departs, ville, jour):
    arrivees_flag = arrivees_departs == ARRIVEES
    invites_participants = get_invites_participants()
    if arrivees_flag:
        vols_objects = InfosVol.objects\
            .filter(date_arrivee=jour, ville_arrivee=ville)\
            .filter(Q(participant__id__isnull=True) |
                    Q(participant__desactive=False))\
            .order_by('heure_arrivee', 'compagnie')
    else:
        vols_objects = InfosVol.objects\
            .filter(date_depart=jour, ville_depart=ville) \
            .filter(Q(participant__id__isnull=True) |
                    Q(participant__desactive=False)) \
            .order_by('heure_depart', 'compagnie')
    arrivees_departs_display = \
        {ARRIVEES: u"Arrivées à", DEPARTS: u"Départs de"}[arrivees_departs]
    vols = SortedDict()
    for vol_object in vols_objects:
        heure, ville, jour = vol_object.get_heure_ville_jour(arrivees_departs)
        vol_key = (heure, vol_object.compagnie, vol_object.numero_vol)
        participants = sorted(vol_object.participants(),
                              key=lambda p: p.get_nom_prenom_sans_accents())
        if participants:
            nb_invites = 0
            for participant in participants:
                participant.invites_vol = invites_participants[participant.id]
                nb_invites += len(participant.invites_vol)
            if vol_key not in vols:
                vols[vol_key] = {
                    'heure': heure,
                    'jour': jour,
                    'ville': ville,
                    'participants': participants,
                    'compagnie': vol_object.compagnie,
                    'numero_vol': vol_object.numero_vol,
                    'nb_invites': nb_invites,
                }
            else:
                vol = vols[vol_key]
                participants_vol = vol['participants']
                participants_vol.extend(participants)
                participants_vol.sort(
                    key=lambda p: p.get_nom_prenom_sans_accents())
                vol['nb_invites'] += nb_invites
    return {
        'arrivees_departs': arrivees_departs,
        'arrivees_departs_display': arrivees_departs_display,
        'jour': jour,
        'ville': ville,
        'vols': vols.values()
    }


def get_dates_arrivees():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT date_arrivee as date_trajet
            FROM gestion_infosvol WHERE date_arrivee is not null
        ORDER BY date_trajet
    ''')
    return [row[0] for row in cursor.fetchall()]


def get_dates_departs():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT date_depart as date_trajet
            FROM gestion_infosvol WHERE date_depart is not null
        ORDER BY date_trajet
    ''')
    return [row[0] for row in cursor.fetchall()]


def get_villes_arrivee():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT ville_arrivee as ville
            FROM gestion_infosvol WHERE ville_arrivee is not null
            AND ville_arrivee != \'\'
        ORDER BY ville
    ''')
    return [row[0] for row in cursor.fetchall()]


def get_villes_depart():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT ville_depart as ville
            FROM gestion_infosvol WHERE ville_depart is not null
            AND ville_depart != \'\'
        ORDER BY ville
    ''')
    return [row[0] for row in cursor.fetchall()]


def get_invites_participants(participants=None):
    if not participants:
        invites = Invite.objects.all()
    else:
        invites = Invite.objects.filter(participant__in=participants)
    invites_participants = defaultdict(list)
    for invite in invites:
        invites_participants[invite.participant_id].append(invite)
    return invites_participants

# Petite structure qui nous permet d'avoir "Pas d'hôtel" dans la liste
# des hôtels
HotelInfo = namedtuple('HotelInfo', ('libelle', 'hotel'))


def get_donnees_participants_activites():
    activites = Activite.objects.order_by('libelle').all()
    invites_participants = get_invites_participants()
    participants_activites = SortedDict()
    all_hotels = [HotelInfo(h.libelle, h) for h in Hotel.objects.all()]
    all_hotels += [HotelInfo(u"(Aucun hôtel sélectionné)", None)]
    for activite in activites:
        hotels = SortedDict()
        participants_activites[activite] = hotels
        for hotel_info in all_hotels:
            participants = SortedDict()
            hotels[hotel_info.libelle] = participants
            participations_activite = ParticipationActivite.objects\
                .filter(activite=activite, participant__hotel=hotel_info.hotel,
                        participant__desactive=False)\
                .select_related('participant')\
                .order_by('participant__nom', 'participant__prenom')
            for participation_activite in participations_activite:
                participant = participation_activite.participant
                invites = (invites_participants[participant.id]
                           if participation_activite.avec_invites
                           else [])
                participants[participant] = invites
    return participants_activites


def get_donnees_activites_scientifiques():
    donnees = []
    for activite in ActiviteScientifique.objects.all():
        participants = Participant.actifs.filter(
            activite_scientifique=activite)
        donnees.append(Element(activite.libelle, participants))
    return donnees


def dictfetchall(cursor):
    """Returns all rows from a cursor as a dict
    repris de: https://docs.djangoproject.com/en/1.4/topics/db/sql/"""
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

LigneVol = namedtuple('LigneVol',
                      ('date1', 'heure1',
                       'no_vol', 'compagnie', 'ville1',
                       'dep_arr', 'genre', 'nom', 'prenom',
                       'vers_de', 'ville2', 'date2',
                       'vol_groupe_id', 'vol_groupe_nom',
                       'participant_id',
                       'nom_normalise', 'prenom_normalise',
                       'prise_en_charge_transport', 'prise_en_charge_sejour'))


def ligne_vol_key(ligne):
    return (ligne.date1, ligne.heure1 if ligne.heure1 else datetime.time(0, 0),
            ligne.nom_normalise, ligne.prenom_normalise)

ARRIVEE_STR = u"Arrivée"
DEPART_STR = u"Départ"
VERS_STR = u"vers"
DE_STR = u"de"


def get_donnees_tous_vols(filtre_ville_depart=None,
                          filtre_ville_arrivee=None):
    params = []
    SQL_vols_non_groupes = """
        SELECT date_depart, heure_depart, ville_depart, date_arrivee,
            heure_arrivee, ville_arrivee, numero_vol, compagnie, genre,
            p.id as participant_id,
            p.nom, prenom, NULL as vol_groupe_id, NULL as vol_groupe_nom,
            prise_en_charge_transport, prise_en_charge_sejour
        FROM gestion_infosvol iv
            LEFT JOIN gestion_participant p on iv.participant_id = p.id
                AND ((p.transport_organise_par_auf = 1
                     AND iv.type_infos = {VOL_ORGANISE}) OR
                     (p.transport_organise_par_auf = 0 AND
                      iv.type_infos IN ({ARRIVEE_SEULEMENT},
                                        {DEPART_SEULEMENT})))
            WHERE iv.vol_groupe_id IS NULL
              AND ((date_depart is NOT NULL AND IFNULL(ville_depart, '') != '')
                OR (date_arrivee is NOT NULL AND
                    IFNULL(ville_arrivee, '') != '')
              )
              AND p.desactive=0""".format(VOL_ORGANISE=VOL_ORGANISE,
                                          ARRIVEE_SEULEMENT=ARRIVEE_SEULEMENT,
                                          DEPART_SEULEMENT=DEPART_SEULEMENT)
    SQL_vols_groupes = """
        SELECT date_depart, heure_depart, ville_depart, date_arrivee,
            heure_arrivee, ville_arrivee, numero_vol, compagnie, genre,
            p.id as participant_id, p.nom,
            prenom, vg.id as vol_groupe_id, vg.nom as vol_groupe_nom,
            prise_en_charge_transport, prise_en_charge_sejour
        FROM (
            gestion_infosvol iv
            INNER JOIN gestion_volgroupe vg ON iv.vol_groupe_id = vg.id
        )
        INNER JOIN gestion_participant p ON p.vol_groupe_id = vg.id
        WHERE p.desactive=0 AND p.transport_organise_par_auf=1"""
    if filtre_ville_depart:
        SQL_vols_non_groupes += ' AND ville_depart = %s'
        SQL_vols_groupes += ' AND ville_depart = %s'
        params += [filtre_ville_depart]
    if filtre_ville_arrivee:
        SQL_vols_non_groupes += ' AND ville_arrivee = %s'
        SQL_vols_groupes += ' AND ville_arrivee = %s'
        params += [filtre_ville_arrivee]
    if params:
        params *= 2
    SQL_vols = '{0} UNION {1}'.format(SQL_vols_non_groupes, SQL_vols_groupes)
    cursor = connection.cursor()
    if params:
        cursor.execute(SQL_vols, params)
    else:
        cursor.execute(SQL_vols)

    dataset = dictfetchall(cursor)
    vols = []
    for row in dataset:
        if row['date_arrivee']:
            ligne_arrivee = LigneVol(
                date1=row['date_arrivee'],
                heure1=row['heure_arrivee'] or "",
                no_vol=row['numero_vol'],
                compagnie=row['compagnie'],
                ville1=row['ville_arrivee'],
                dep_arr=ARRIVEE_STR,
                genre=row['genre'],
                nom=row['nom'],
                prenom=row['prenom'],
                vers_de=DE_STR,
                ville2=row['ville_depart'],
                date2=row['date_depart'],
                vol_groupe_id=row['vol_groupe_id'],
                vol_groupe_nom=row['vol_groupe_nom'],
                participant_id=row['participant_id'],
                nom_normalise=strip_accents(row['nom']),
                prenom_normalise=strip_accents(row['prenom']),
                prise_en_charge_transport=row['prise_en_charge_transport'],
                prise_en_charge_sejour=row['prise_en_charge_sejour'],
            )
            vols.append(ligne_arrivee)
        if row['date_depart']:
            ligne_depart = LigneVol(
                date1=row['date_depart'],
                heure1=row['heure_depart'] or "",
                no_vol=row['numero_vol'],
                compagnie=row['compagnie'],
                ville1=row['ville_depart'],
                dep_arr=DEPART_STR,
                genre=row['genre'],
                nom=row['nom'],
                prenom=row['prenom'],
                vers_de=VERS_STR,
                ville2=row['ville_arrivee'],
                date2=row['date_arrivee'],
                vol_groupe_id=row['vol_groupe_id'],
                vol_groupe_nom=row['vol_groupe_nom'],
                participant_id=row['participant_id'],
                nom_normalise=strip_accents(row['nom']),
                prenom_normalise=strip_accents(row['prenom']),
                prise_en_charge_transport=row['prise_en_charge_transport'],
                prise_en_charge_sejour=row['prise_en_charge_sejour'],
            )
            vols.append(ligne_depart)
    vols.sort(key=ligne_vol_key)
    return vols


PaiementParticipant = namedtuple('PaiementParticipant', (
    'P_actif', 'P_id', 'P_genre', 'P_nom', 'P_prenom', 'P_poste',
    'P_courriel', 'P_adresse', 'P_ville', 'P_pays', 'P_code_postal',
    'P_telephone', 'P_telecopieur', 'P_invites', 'P_fonction', 'P_region',
    'E_cgrm', 'E_nom', 'E_delinquant', 'f_PEC_I', 'f_total_I',
    'f_fact_I', 'f_PEC_T', 'f_AUF_T', 'f_total_T', 'f_fact_T', 'f_PEC_S',
    'f_AUF_S', 'f_total_S', 'f_fact_S', 'f_supp_S', 'f_PEC_A', 'f_total_A',
    'f_valide', 'f_TOTAL', 'f_mode', 'f_accompte', 'f_solde', 
    'n_R', 'n_N', 'n_T', 'n_A', 'n_total', 'n_mode', 'n_statut',))


def format_money(n):
    return u'{0:.2f}'.format(n).replace('.', ',')


def bool_to_o_n(b):
    return u"O" if b else u"N"


def get_donnees_paiements(actifs_seulement):
    frais_participants = defaultdict(partial(defaultdict, lambda: 0))
    for f in Frais.objects.select_related('type_frais').all():
        frais_participants[f.participant_id][f.type_frais.code] = f.total()
    notes_versees = set(v[0] for v in
                        PointDeSuivi.objects.get(
                            code=consts.POINT_DE_SUIVI_NOTE_VERSEE)
                        .participant_set.values_list('id'))

    participants = (Participant.actifs.all() if actifs_seulement else
                    Participant.objects.all())
    participants = participants.sql_extra_fields(
        'delinquant', 'frais_inscription', 'frais_inscription_facture',
        'frais_transport', 'frais_transport_facture', 'frais_hebergement',
        'frais_hebergement_facture', 'forfaits_invites',
        'frais_autres', 'total_frais',
        'total_facture', 'solde').order_by('nom', 'prenom')\
        .select_related('etablissement', 'etablissement__pays',
                        'etablissement__region', 'institution__region',
                        'fonction', 'fonction__type_institution',
                        'implantation')\
        .prefetch_related(
        Prefetch('paiement_set',
                 queryset=Paiement.objects.select_related('implantation')),
        'forfaits',
        'inscription__paypalresponse_set',
        Prefetch('inscription__paypalresponse_set',
                 to_attr='accepted_paypal_responses',
                 queryset=PaypalResponse.objects.all_accepted())
    )
    # on sépare le count car une annotation sur la requête principale
    # produit un SQL atroce.
    nombre_invites = dict(
        (p['id'], p['num_invites']) for p in
        Participant.objects.values('id').annotate(num_invites=Count('invite')))

    forfaits = get_forfaits()
    result = []
    for p in participants:
        frais = frais_participants[p.id]
        pp = PaiementParticipant(
            P_actif=bool_to_o_n(not p.desactive),
            P_id=p.id,
            P_genre=p.get_genre_display(),
            P_nom=p.nom,
            P_prenom=p.prenom,
            P_poste=p.poste,
            P_courriel=p.courriel,
            P_adresse=p.adresse,
            P_ville=p.ville,
            P_pays=p.pays,
            P_code_postal=p.code_postal,
            P_telephone=p.telephone,
            P_telecopieur=p.telecopieur,
            P_fonction=p.fonction.libelle,
            P_invites=nombre_invites[p.id],
            P_region=p.get_region_code(),
            E_cgrm=p.etablissement.id if p.etablissement else u"",
            E_nom=p.nom_institution(),
            E_delinquant=bool_to_o_n(p.delinquant) if p.etablissement
            else u"n/a",
            f_PEC_I=bool_to_o_n(p.prise_en_charge_inscription),
            f_total_I=format_money(p.frais_inscription),
            f_fact_I=format_money(p.frais_inscription_facture),
            f_PEC_T=bool_to_o_n(p.prise_en_charge_transport),
            f_AUF_T=bool_to_o_n(p.transport_organise_par_auf),
            f_total_T=format_money(p.frais_transport),
            f_fact_T=format_money(p.frais_transport_facture),
            f_PEC_S=bool_to_o_n(p.prise_en_charge_sejour),
            f_AUF_S=bool_to_o_n(p.reservation_hotel_par_auf),
            f_total_S=format_money(p.frais_hebergement),
            f_fact_S=format_money(p.frais_hebergement_facture),
            f_supp_S=format_money(
                forfaits[consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE].montant
                if p.a_forfait(consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE)
                else 0),
            f_PEC_A=bool_to_o_n(p.prise_en_charge_activites),
            f_total_A=format_money(p.forfaits_invites),
            f_valide=bool_to_o_n(p.facturation_validee),
            f_mode=p.get_moyens_paiement_display(),
            f_accompte=format_money(p.total_deja_paye),
            f_solde=format_money(p.get_solde()),
            f_TOTAL=format_money(p.total_facture),
            n_R=format_money(frais['repas']),
            n_N=format_money(frais['nuitees']),
            n_T=format_money(frais['taxi']),
            n_A=format_money(frais['autres']),
            n_total=format_money(sum(frais.itervalues())),
            n_mode=p.get_modalite_versement_frais_sejour_display(),
            n_statut=bool_to_o_n(p.id in notes_versees),
        )

        result.append(pp)
    return result


LigneCoupon = namedtuple('LigneCoupon', ('nom', 'type', 'region', 'hotel',
                                         'heure_arrivee', 'compagnie', 'vol',
                                         'nb_passagers', 'autres_passagers'))

EnteteListeCoupons = namedtuple('EnteteListeCoupons',
                                ('depart_arrivee', 'ville', 'date', ))


DEPART = 'depart'
ARRIVEE = 'arrivee'


def make_entree_coupon(participant, depart_arrivee, ville, date_, heure,
                       compagnie, vol):
    noms_invites = participant.get_noms_invites()
    nb_passagers = len(noms_invites) + 1
    entete = EnteteListeCoupons(
        depart_arrivee=depart_arrivee, ville=ville.upper(),
        date=date_)
    ligne = LigneCoupon(
        nom=participant.get_nom_complet(),
        type=participant.get_fonction_libelle(),
        region=participant.get_region_nom(),
        hotel=participant.hotel or u"(Aucun)",
        heure_arrivee=heure,
        compagnie=compagnie,
        vol=vol,
        nb_passagers=nb_passagers,
        autres_passagers=u",".join(noms_invites)
    )
    return entete, ligne


def donnees_liste_coupons():
    participants = participants_avec_vols()
    listes_coupons = defaultdict(list)
    for participant in participants:
        infos_depart_arrivee = participant.get_infos_depart_arrivee()
        if infos_depart_arrivee.depart_date and infos_depart_arrivee.depart_de:
            entete_depart, ligne_depart = make_entree_coupon(
                participant, DEPART,
                infos_depart_arrivee.depart_de,
                infos_depart_arrivee.depart_date,
                infos_depart_arrivee.depart_heure,
                infos_depart_arrivee.depart_compagnie,
                infos_depart_arrivee.depart_vol)
            listes_coupons[entete_depart].append(ligne_depart)
        if infos_depart_arrivee.arrivee_date and infos_depart_arrivee.arrivee_a:
            entete_arrivee, ligne_arrivee = make_entree_coupon(
                participant, ARRIVEE, infos_depart_arrivee.arrivee_a,
                infos_depart_arrivee.arrivee_date,
                infos_depart_arrivee.arrivee_heure,
                infos_depart_arrivee.arrivee_compagnie,
                infos_depart_arrivee.arrivee_vol)
            listes_coupons[entete_arrivee].append(ligne_arrivee)
    return sorted(listes_coupons.iteritems(), key=lambda item: item[0])


def participants_avec_vols():
    return Participant.actifs \
        .select_related('vol_groupe', 'etablissement', 'implantation',
                        'fonction', 'fonction__type_institution',
                        'etablissement__region', 'implantation__region',
                        'hotel', 'institution', 'institution__region') \
        .prefetch_related('infosvol_set', 'vol_groupe__infosvol_set',
                          'invite_set', 'fichier_set') \
        .order_by('nom', 'prenom')


EnteteListeHotel = namedtuple('EnteteListeHotel', ('hotel', 'arrivee_date'))
LigneListeHotel = namedtuple('LigneListeHotel',
                             ('nom', 'type', 'PEC', 'occupants',
                              'nuitees', 'aeroport', 'heure_checkin',
                              'depart_datetime', 'passeport'))


def donnees_liste_hotels():
    participants = participants_avec_vols()
    listes_hotels = defaultdict(list)
    casablanca = consts.CASABLANCA.lower()
    for participant in participants:
        infos_depart_arrivee = participant.get_infos_depart_arrivee()
        arrivee_date = (participant.date_arrivee_hotel or
                        infos_depart_arrivee.arrivee_date)
        depart_date = (participant.date_depart_hotel or
                       infos_depart_arrivee.depart_date)
        if arrivee_date and participant.hotel:
            if (infos_depart_arrivee.arrivee_a and
                    infos_depart_arrivee.arrivee_heure):
                dt_checkin = datetime.datetime.combine(
                    infos_depart_arrivee.arrivee_date,
                    infos_depart_arrivee.arrivee_heure)
                dt_checkin += datetime.timedelta(hours=1)
                if infos_depart_arrivee.arrivee_a.lower() == casablanca:
                    dt_checkin += datetime.timedelta(hours=2)
                heure_checkin = dt_checkin.time()
            else:
                heure_checkin = None

            if depart_date and arrivee_date:
                nuitees = (depart_date - arrivee_date).days
            else:
                nuitees = None

            if (depart_date and infos_depart_arrivee.depart_heure and
                    infos_depart_arrivee.depart_de):
                depart_heure = infos_depart_arrivee.depart_heure
                depart_datetime = datetime.datetime.combine(depart_date,
                                                            depart_heure)
                depart_datetime -= datetime.timedelta(hours=1)
                if infos_depart_arrivee.depart_de.lower() == casablanca:
                    depart_datetime -= datetime.timedelta(hours=2)
            else:
                depart_datetime = None

            entete = EnteteListeHotel(participant.hotel.libelle, arrivee_date)

            ligne = LigneListeHotel(
                nom=participant.get_nom_complet(),
                type=participant.get_fonction_libelle(),
                PEC=u"AUF" if participant.prise_en_charge_sejour else u"",
                occupants=len(participant.invite_set.all()) + 1,
                nuitees=nuitees,
                aeroport=infos_depart_arrivee.arrivee_a,
                heure_checkin=heure_checkin,
                depart_datetime=depart_datetime,
                passeport=u"oui" if participant.a_televerse_passeport()
                else u"-"
            )
            listes_hotels[entete].append(ligne)
    return sorted(listes_hotels.iteritems(), key=lambda item: item[0])
