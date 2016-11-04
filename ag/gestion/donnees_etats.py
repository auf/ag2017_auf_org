# -*- encoding: utf-8 -*-
from collections import namedtuple, defaultdict
from functools import partial
from itertools import groupby
import datetime

from ag.gestion import consts
from ag.gestion.consts import ARRIVEES, DEPARTS, VOL_ORGANISE, DEPART_SEULEMENT, ARRIVEE_SEULEMENT
from ag.gestion.models import (Participant, InfosVol, Invite, Activite, Hotel,
                               ParticipationActivite, ActiviteScientifique,
                               strip_accents, Frais, PointDeSuivi)
from django.db import connection
from django.db.models import Q, Count
from django.utils.datastructures import SortedDict

from ag.inscription.models import get_forfaits

Element = namedtuple('DonneeEtat', ['titre', 'elements'])


def get_donnees_etat_participants():
    def get_participants_etablissements():
        participants = Participant.actifs\
            .filter(type_institution=Participant.ETABLISSEMENT)\
            .select_related('etablissement', 'etablissement__pays',
                            'statut')\
            .order_by('etablissement__pays__nom', 'etablissement__nom',
                      'statut__ordre', 'nom', 'prenom')
        return recursive_group_by(
            list(participants),
            keys=[lambda p:p.etablissement.pays,
                  lambda p: p.etablissement,
                  lambda p:p.statut],
            titles=[lambda p: p.nom, lambda e: e.nom, lambda s: s.libelle])

    def get_observateurs():
        participants = Participant.actifs \
            .filter(type_institution=Participant.AUTRE_INSTITUTION,
                    statut__code='obs') \
            .select_related('region') \
            .order_by('nom_autre_institution', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.nom_autre_institution, p.get_region())],
            titles=[lambda k: u"{0}, {1}".format(k[0], k[1].nom)])

    def get_instances():
        participants = Participant.actifs \
            .filter(type_institution=Participant.INSTANCE_AUF)\
            .order_by('instance_auf', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.instance_auf, p.get_instance_auf_display())],
            titles=[lambda k: k[1]]
        )

    def get_personnel_auf():
        participants = Participant.actifs \
            .filter(type_institution=Participant.AUTRE_INSTITUTION,
                    statut__code='pers_auf') \
            .select_related('region')\
            .order_by('nom_autre_institution', 'region__nom', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: p.nom_autre_institution,
                  lambda p: p.region],
            titles=[lambda k: k, lambda k: k.nom]
        )

    def get_autres():
        participants = Participant.actifs \
            .filter(type_institution=Participant.AUTRE_INSTITUTION)\
            .exclude(statut__code='pers_auf') \
            .exclude(statut__code='obs') \
            .select_related('region') \
            .order_by('nom_autre_institution', 'region__nom', 'nom', 'prenom')
        return recursive_group_by(
            participants,
            keys=[lambda p: (p.nom_autre_institution, p.get_region())],
            titles=[lambda k: u"{0}, {1}".format(k[0], k[1].nom)])

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
    'P_telephone', 'P_telecopieur', 'P_statut', 'E_cgrm', 'E_nom',
    'E_delinquant', 'P_invites', 'f_PEC_I', 'f_total_I', 'f_fact_I', 'f_PEC_T',
    'f_AUF_T', 'f_total_T', 'f_fact_T', 'f_PEC_S', 'f_AUF_S', 'f_total_S',
    'f_fact_S', 'f_supp_S', 'f_PEC_A', 'f_total_A', 'f_valide',
    'f_mode', 'f_accompte', 'f_solde', 'n_R', 'n_N', 'n_T', 'n_A', 'n_total',
    'n_mode', 'n_statut',))


def format_money(n):
    return u'{0:.2f}'.format(n).replace('.', ',')


def get_donnees_paiements(actifs_seulement):
    frais_participants = defaultdict(partial(defaultdict, lambda: 0))
    for f in Frais.objects.select_related('type_frais').all():
        frais_participants[f.participant_id][f.type_frais.code] = f.total()
    notes_versees = set(v[0] for v in
                        PointDeSuivi.objects.get(id=7)
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
                        'etablissement__region', 'region', 'statut',
                        'type_autre_institution')
    # on sépare le count car une annotation sur la requête principale
    # produit un SQL atroce.
    nombre_invites = dict(
        (p['id'], p['num_invites']) for p in
        Participant.objects.values('id').annotate(num_invites=Count('invite')))

    bool_ON = lambda b: u"O" if b else u"N"
    forfaits = get_forfaits()
    result = []
    for p in participants:
        frais = frais_participants[p.id]
        pp = PaiementParticipant(
            P_actif=bool_ON(not p.desactive),
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
            P_statut=p.statut.libelle,
            E_cgrm=p.etablissement.id if p.etablissement else u"",
            E_nom=p.nom_institution(),
            E_delinquant=bool_ON(p.delinquant) if p.etablissement else u"n/a",
            P_invites=nombre_invites[p.id],
            f_PEC_I=bool_ON(p.prise_en_charge_inscription),
            f_total_I=format_money(p.frais_inscription),
            f_fact_I=format_money(p.frais_inscription_facture),
            f_PEC_T=bool_ON(p.prise_en_charge_transport),
            f_AUF_T=bool_ON(p.transport_organise_par_auf),
            f_total_T=format_money(p.frais_transport),
            f_fact_T=format_money(p.frais_transport_facture),
            f_PEC_S=bool_ON(p.prise_en_charge_sejour),
            f_AUF_S=bool_ON(p.reservation_hotel_par_auf),
            f_total_S=format_money(p.frais_hebergement),
            f_fact_S=format_money(p.frais_hebergement_facture),
            f_supp_S=format_money(
                forfaits[consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE].montant
                if p.a_forfait(consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE)
                else 0),
            f_PEC_A=bool_ON(p.prise_en_charge_activites),
            f_total_A=format_money(p.forfaits_invites),
            f_valide=bool_ON(p.facturation_validee),
            f_mode=p.get_paiement_display(),
            f_accompte=format_money(p.accompte),
            f_solde=format_money(p.total_facture - p.accompte),
            n_R=format_money(frais['repas']),
            n_N=format_money(frais['nuitees']),
            n_T=format_money(frais['taxi']),
            n_A=format_money(frais['autres']),
            n_total=format_money(sum(frais.itervalues())),
            n_mode=p.get_modalite_versement_frais_sejour_display(),
            n_statut=bool_ON(p.id in notes_versees),
        )

        result.append(pp)
    return result
