# -*- encoding: utf-8 -*-

import collections
import urllib
import operator
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import (
    Fonction,
    Participant,
    PointDeSuivi,
    Activite,
    EN_COURS,
)

from ag.gestion import forms, consts

from ag.reference.models import (
    Region,
    Etablissement,
    CODE_ETAB_ENSEIGNEMENT,
    CODE_CENTRE_RECHERCHE,
    CODE_RESEAU,
    CODE_ASSOCIE,
    CODE_TITULAIRE,
)


def nb_par_region(participants, category_fn):
    pairs = [(category_fn(p), p.get_region_id())
             for p in participants]
    # noinspection PyArgumentList
    return collections.Counter(pairs)


def nb_par_categorie(participants, category_fn):
    # noinspection PyArgumentList
    return collections.Counter([category_fn(p) for p in participants])


SumData = collections.namedtuple('SumData', ('sum', 'search_url'))


def make_sum_data(sum_, search_params):
    search_url = u"{}?{}".format(reverse('participants'),
                                 urllib.urlencode(search_params), )
    return SumData(sum=sum_,
                   search_url=search_url)


SumsLine = collections.namedtuple('SumsLine', ('label', 'sums'))


def table_fonctions_regions(participants, fonctions, regions):
    fonction_getter = operator.attrgetter('fonction_id')
    region_counter = nb_par_region(participants, fonction_getter)
    cat_counter = nb_par_categorie(participants, fonction_getter)
    sums_lines = []
    for fonction in fonctions:
        sum_data = make_sum_data(cat_counter[fonction.id],
                                 {'fonction': fonction.id})
        sums = [sum_data]
        for region in regions:
            sum_data = make_sum_data(region_counter[(fonction.id, region.id)],
                                     {'fonction': fonction.id,
                                      'region': region.id})
            sums.append(sum_data)
        sum_data = make_sum_data(region_counter[(fonction.id, None)],
                                 {'fonction': fonction.id,
                                  'region': forms.AUCUNE_REGION})
        sums.append(sum_data)
        sums_lines.append(SumsLine(fonction.libelle, sums))

    return sums_lines


def statut_getter(participant):
    return participant.etablissement.statut


def statut_qualite_getter(participant):
    return participant.etablissement.statut, participant.etablissement.qualite


def table_membres(participants, regions):
    participants = [p for p in participants if p.represente_etablissement]
    statut_counter = nb_par_categorie(participants, statut_getter)
    statut_qualite_counter = nb_par_categorie(participants,
                                              statut_qualite_getter)
    statut_region_counter = nb_par_region(participants, statut_getter)
    statut_qualite_region_counter = nb_par_region(participants,
                                                  statut_qualite_getter)
    sums_lines = []
    libelles_statuts = dict(Etablissement.STATUT_CHOICES)
    for statut in (CODE_TITULAIRE, CODE_ASSOCIE):
        sums = [make_sum_data(statut_counter[statut], {'statut': statut})]
        for region in regions:
            sums.append(make_sum_data(statut_region_counter[statut, region.id],
                                      {'statut': statut, 'region': region.id}))

        sums_lines.append(SumsLine(libelles_statuts[statut], sums))
        for qualite in (CODE_ETAB_ENSEIGNEMENT, CODE_CENTRE_RECHERCHE,
                        CODE_RESEAU):
            statut_qualite_params = {'statut': statut, 'qualite': qualite}
            sums = [make_sum_data(statut_qualite_counter[(statut, qualite)],
                                  statut_qualite_params)]
            for region in regions:
                counter_id = (statut, qualite), region.id
                sum_ = statut_qualite_region_counter[counter_id]
                params = dict(region=region.id, **statut_qualite_params)
                sum_data = make_sum_data(sum_, params)
                sums.append(sum_data)
            libelle = mark_safe(u'<span class="qualite">{}</span>'
                                .format(qualite))
            sums_lines.append(SumsLine(libelle, sums))
    return sums_lines


def ligne_regions(participants, regions):
    # noinspection PyArgumentList
    counter = collections.Counter((p.get_region_id() for p in participants))
    sums = [make_sum_data(len(participants), {})]
    for region in regions:
        sums.append(make_sum_data(counter[region.id], {'region': region.id}))
    sums.append(make_sum_data(counter[None], {'region': forms.AUCUNE_REGION}))
    return SumsLine(label=u"Tous", sums=sums)


CritereTableau = collections.namedtuple(
    'CritereTableau', ('code', 'category_fn', 'search_params'))


CATEGORIES_VOTANTS = (
    (u'Titulaire', lambda p: p.etablissement.statut == consts.CODE_TITULAIRE,
     {'statut': consts.CODE_TITULAIRE, 'votant': 'on'}),
    (u'Associé', lambda p: p.etablissement.statut == consts.CODE_ASSOCIE,
     {'statut': consts.CODE_ASSOCIE, 'votant': 'on'}),
    (u'Réseau', lambda p: p.etablissement.qualite == consts.CODE_RESEAU,
     {'qualite': consts.CODE_RESEAU, 'votant': 'on'}),
)


def categories_votants():
    return [CritereTableau(*d) for d in CATEGORIES_VOTANTS]


def localisation_votants():
    def critere_region(code_region):
        return CritereTableau(
            code=consts.REGIONS_VOTANTS_DICT[code_region],
            category_fn=lambda p: p.get_region_vote() == code_region,
            search_params={'region_vote': code_region})

    def critere_pays(code_pays, nom_pays):
        return CritereTableau(
            code=nom_pays,
            category_fn=lambda p: p.etablissement.pays.code == code_pays,
            search_params={'pays_code': code_pays})

    return (
        critere_region(consts.REG_AFRIQUE),
        critere_region(consts.REG_AMERIQUES),
        critere_pays(consts.CODE_PAYS_CANADA, u"dont Canada"),
        critere_region(consts.REG_ASIE_PACIFIQUE),
        critere_region(consts.REG_EUROPE_EST),
        critere_region(consts.REG_EUROPE_OUEST),
        critere_pays(consts.CODE_PAYS_FRANCE, u"dont France"),
        critere_region(consts.REG_MAGHREB),
        critere_region(consts.REG_MOYEN_ORIENT),
    )


def table_votants(participants):
    # votants = [p for p in participants
    #            if p.fonction.code == consts.FONCTION_REPR_UNIVERSITAIRE]
    votants = [p for p in participants
               if p.inscription and p.inscription.est_pour_mandate()]
    pairs = []
    criteres_localisation = localisation_votants()
    criteres_categorisation = categories_votants()
    for p in votants:
        for localisation in criteres_localisation:
            if localisation.category_fn(p):
                for categorie in criteres_categorisation:
                    if categorie.category_fn(p):
                        pairs.append((categorie.code, localisation.code))
        for categorie in criteres_categorisation:
            if categorie.category_fn(p):
                pairs.append(categorie.code)
    # noinspection PyArgumentList
    counter = collections.Counter(pairs)
    lignes = []
    for categorie in criteres_categorisation:
        sums = [make_sum_data(counter[categorie.code], categorie.search_params)]
        for localisation in criteres_localisation:
            search_params = categorie.search_params.copy()
            search_params.update(localisation.search_params)
            sum_data = make_sum_data(
                counter[(categorie.code, localisation.code)], search_params)
            sums.append(sum_data)
        lignes.append(SumsLine(categorie.code, sums))
    return (lignes, [c.code for c in criteres_categorisation],
            [c.code for c in criteres_localisation])


def table_points_de_suivi(participants, points_de_suivi, regions):
    pairs = []
    for p in participants:
        region_id = p.get_region_id()
        for pds in p.suivi.all():
            pairs.append((region_id, pds.id))
            pairs.append(pds.id)
    # noinspection PyArgumentList
    counter = collections.Counter(pairs)
    lignes = []
    for pds in points_de_suivi:
        sums = [make_sum_data(counter[pds.id], {'suivi': pds.id})]
        for region in regions:
            params = {'suivi': pds.id, 'region': region.id}
            sums.append(make_sum_data(counter[(region.id, pds.id)], params))
        sums.append(make_sum_data(counter[(None, pds.id)],
                                  {'suivi': pds.id,
                                   'region': forms.AUCUNE_REGION}))
        lignes.append(SumsLine(pds.libelle, sums))
    return lignes


def criteres_prise_en_charge():
    return (
        CritereTableau(u"Frais d'inscription",
                       lambda p: p.prise_en_charge_inscription,
                       {'prise_en_charge_inscription': forms.PEC_ACCEPTEE}),
        CritereTableau(u"Transport",
                       lambda p: p.prise_en_charge_transport,
                       {'prise_en_charge_transport': forms.PEC_ACCEPTEE}),
        CritereTableau(mark_safe(u"<span class=\"qualite\">Complétée</span>"),
                       lambda p: (p.prise_en_charge_transport and
                                  p.statut_dossier_transport == EN_COURS),
                       {'prise_en_charge_transport': forms.PEC_ACCEPTEE,
                        'statut_dossier_transport': EN_COURS}),
        CritereTableau(mark_safe(u"<span class=\"qualite\">À traiter</span>"),
                       lambda p: p.transport_non_organise,
                       {'probleme': 'transport_non_organise', }),
        CritereTableau(u"Hébergement",
                       lambda p: p.prise_en_charge_sejour,
                       {'prise_en_charge_sejour': forms.PEC_ACCEPTEE}),
        CritereTableau(mark_safe(u"<span class=\"qualite\">Complétée </span>"),
                       lambda p: (
                       p.prise_en_charge_sejour and not p.hotel_manquant and
                       not p.nb_places_incorrect),
                       {}),
        CritereTableau(mark_safe(u"<span class=\"qualite\">À traiter </span>"),
                       lambda p: p.hotel_manquant,
                       {'probleme': 'hotel_manquant'}),
        CritereTableau(mark_safe(u"<span class=\"qualite\">"
                                 u"Occupation incorrecte</span>"),
                       lambda p: p.nb_places_incorrect,
                       {'probleme': 'nb_places_incorrect'}),
    )

PROBLEMES_TABLEAU_DE_BORD = (
    'transport_non_organise',
    'hotel_manquant',
    'nb_places_incorrect',
    'paiement_en_trop',
    'solde_a_payer',
    'delinquant',
)


def table_prise_en_charge(participants, regions):
    criteres = criteres_prise_en_charge()
    return make_sums_lines(participants, criteres, regions)


def make_sums_lines(participants, criteres, regions):
    pairs = []
    for p in participants:
        region_id = p.get_region_id()
        for critere in criteres:
            if critere.category_fn(p):
                pairs.append((region_id, critere.code))
                pairs.append(critere.code)
    # noinspection PyArgumentList
    counter = collections.Counter(pairs)
    lignes = []
    for critere in criteres:
        sums = [make_sum_data(counter[critere.code], critere.search_params)]
        for region in regions:
            params = critere.search_params.copy()
            params.update({'region': region.id})
            sum_data = make_sum_data(counter[(region.id, critere.code)], params)
            sums.append(sum_data)
        params = critere.search_params.copy()
        params.update({'region': forms.AUCUNE_REGION})
        sums.append(make_sum_data(counter[(None, critere.code)], params))
        lignes.append(SumsLine(critere.code, sums))
    return lignes


def criteres_paiement():
    return (
        CritereTableau(u"Cotisation impayée (3 ans en plus)",
                       lambda p: p.delinquant,
                       {'probleme': 'delinquant'}),
        CritereTableau(u"Solde impayé",
                       lambda p: p.solde_a_payer,
                       {'probleme': 'solde_a_payer'}),
        CritereTableau(u"Aucun solde à payer",
                       lambda p: not p.solde_a_payer and not p.paiement_en_trop,
                       {'pas_de_solde_a_payer': 'on'}),
        CritereTableau(u"Paiement en trop",
                       lambda p: p.paiement_en_trop,
                       {'probleme': 'paiement_en_trop'}),
        CritereTableau(u"Paiement NDF nécessaire",
                       lambda p: p.presence_frais and not p.note_versee,
                       {'paiement_ndf': 'on'}),
    )


def table_paiements(participants, regions):
    criteres = criteres_paiement()
    return make_sums_lines(participants, criteres, regions)


def table_activites(participants, activites, regions):
    pairs = []
    for p in participants:
        region_id = p.get_region_id()
        for pa in p.participationactivite_set.all():
            pairs.append((region_id, pa.activite_id))
            pairs.append(pa.activite_id)
            if pa.avec_invites:
                nb_invites = p.nombre_invites()
                pairs.extend(
                    [(region_id, pa.activite_id), pa.activite_id] * nb_invites)
    # noinspection PyArgumentList
    counter = collections.Counter(pairs)
    lignes = []
    for activite in activites:
        sums = [make_sum_data(counter[activite.id], {'activite': activite.id})]
        for region in regions:
            params = {'activite': activite.id, 'region': region.id}
            sums.append(make_sum_data(counter[(region.id, activite.id)],
                                      params))
        sums.append(make_sum_data(counter[(None, activite.id)],
                                  {'activite': activite.id,
                                   'region': forms.AUCUNE_REGION}))
        lignes.append(SumsLine(activite.libelle, sums))
    return lignes


def get_donnees():
    fonctions = Fonction.objects.all()
    regions = Region.objects.all()
    points_de_suivi = PointDeSuivi.objects.all()
    activites = Activite.objects.all()
    participants = Participant.actifs\
        .defer('nom', 'prenom', 'nationalite', 'poste', 'courriel',
               'adresse', 'ville', 'pays', 'code_postal', 'telephone',
               'telecopieur', 'notes_facturation', 'notes',
               'notes_hebergement', 'modalite_versement_frais_sejour',
               'numero_facture', 'numero_dossier_transport',)\
        .select_related('etablissement__region', 'fonction',
                        'etablissement__pays',
                        'fonction__type_institution',
                        'implantation__region', 'institution__region',
                        'inscription__invitation')\
        .avec_problemes(*PROBLEMES_TABLEAU_DE_BORD)\
        .avec_presence_frais()\
        .prefetch_related('suivi', 'participationactivite_set',
                          'invite_set')\
        .distinct()
    participants = list(participants)
    totaux_regions = ligne_regions(participants, regions)
    par_fonction = table_fonctions_regions(participants, fonctions, regions)
    par_statut_qualite = table_membres(participants, regions)
    par_region_vote, categories_electeurs, localisations_electeurs = \
        table_votants(participants)
    par_point_de_suivi = table_points_de_suivi(participants, points_de_suivi,
                                               regions)
    par_prise_en_charge = table_prise_en_charge(participants, regions)
    par_statut_paiement = table_paiements(participants, regions)
    par_activite = table_activites(participants, activites, regions)
    return {
        'totaux_regions': totaux_regions,
        'par_fonction': par_fonction,
        'par_statut_qualite': par_statut_qualite,
        'par_region_vote': par_region_vote,
        'categories_electeurs': categories_electeurs,
        'localisations_electeurs': localisations_electeurs,
        'par_point_de_suivi': par_point_de_suivi,
        'par_prise_en_charge': par_prise_en_charge,
        'par_statut_paiement': par_statut_paiement,
        'par_activite': par_activite,
        'regions': regions,
    }
