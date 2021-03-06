# -*- encoding: utf-8 -*-
import collections

from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.shortcuts import render

from ag.elections.models import (
    get_electeur_criteria, get_donnees_liste_salle,
    get_all_listes_candidat_criteria, Election, filter_participants,
    get_donnees_bulletin_ca, get_donnees_bulletin_cass_tit,
    get_donnees_bulletin, ParticipantModified, get_candidatures_criteria,
    get_candidats_possibles, Candidats, CRITERE_TOUS, CATEGORIES_ELECTIONS)
from ag.gestion import consts
from ag.gestion.consts import ELU
from .forms import CandidatureFormset


LigneCandidature = collections.namedtuple(
    'LigneCandidature', ('candidat', 'form'))


def make_candidatures_template_data(post_data, code_critere, elections):
    criteres_candidatures = get_candidatures_criteria()
    try:
        critere = criteres_candidatures[code_critere]
    except KeyError:
        raise Http404()

    candidats = get_candidats_possibles(critere.filter)
    if critere.une_seule_region:
        candidats_editables = Candidats([c for c in candidats
                                         if c.statut != ELU])
    else:
        candidats_editables = candidats
    candidatures_formset = CandidatureFormset(post_data,
                                              candidats=candidats_editables,
                                              elections=elections)
    lignes = []
    for candidat in candidats.grouped_by_region():
        form = candidatures_formset.get_form_by_participant_id(
            candidat.participant_id)
        lignes.append(LigneCandidature(candidat=candidat,
                                       form=form))
    return {'formset': candidatures_formset,
            'lignes': lignes,
            'critere': critere,
            'une_seule_region': critere.une_seule_region,
            'elections': elections,
            'criteres_candidatures': criteres_candidatures,
            }


def candidatures(request, code_critere=CRITERE_TOUS):
    if request.is_ajax():
        template = "elections/candidatures_form.html"
    else:
        template = "elections/candidatures.html"
    elections = list(Election.objects.all())
    template_data = make_candidatures_template_data(request.POST or None,
                                                    code_critere, elections)
    message_echec = ""
    if request.method == 'POST':
        candidatures_formset = template_data['formset']
        if candidatures_formset.is_valid():
            candidats_edited = candidatures_formset.get_updated_candidats()
            try:
                candidats_edited.update_participants()
            except ParticipantModified as e:
                message_echec = e.message
            template_data = make_candidatures_template_data(
                None, code_critere, elections)
        else:
            message_echec = candidatures_formset.errors
        template_data['message_echec'] = message_echec
    return render(request, template, template_data)


SALLE = 'salle'
EMARGEMENT = 'emargement'


def liste_votants(request, code_critere, salle_ou_emargement):
    criteria = get_electeur_criteria()
    critere = critere_or_404(code_critere, criteria)
    donnees = get_donnees_liste_salle(critere)
    template = "elections/liste_{}/{}.html".format(
        salle_ou_emargement, critere.code)
    return render(request, template, {
        'participants_par_pays': donnees,
        'titre_critere': critere.titre,
    })


def critere_or_404(code_critere, criteria):
    try:
        critere = criteria[code_critere]
    except KeyError:
        raise Http404()
    return critere

NOMS_ELECTIONS_LISTES_CANDIDATS = {
    consts.ELEC_PRES: "Présidence",
    consts.ELEC_CA: "Membres universitaires du Conseil d’administration et "
                    "leur suppléants",
    consts.ELEC_CASS_TIT: "Représentants des membres titulaires du Conseil "
                          "associatif",
    consts.ELEC_CASS_ASS: "Représentants des membres Associés du Conseil "
                          "associatif",
    consts.ELEC_CASS_RES: "Représentants des réseaux institutionnels du "
                          "Conseil associatif",
}


def liste_candidats(request, code_critere):
    elections = Election.objects.all()
    criteria = get_all_listes_candidat_criteria(elections)
    critere = critere_or_404(code_critere, criteria)
    participants = filter_participants(critere.filter)
    participants = participants.order_by('nom', 'prenom', )\
        .select_related('etablissement')
    if critere.code_region:
        nom_region = consts.REGIONS_VOTANTS_DICT[critere.code_region]
    else:
        nom_region = ""
    return render(
        request,
        "elections/liste_candidats/base.html",
        {
            'participants': participants,
            'titre_critere': critere.titre,
            'nom_election': NOMS_ELECTIONS_LISTES_CANDIDATS[
                critere.code_election],
            'nom_region': nom_region,
            'election_ca': critere.code_election == consts.ELEC_CA,
        })


def bulletin_ca(request):
    candidats_par_region, nb_sieges_total = get_donnees_bulletin_ca()
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[consts.ELEC_CA]
    return render(request, 'elections/bulletin/ca.html',
                  {'nom_election': nom_election,
                   'regions': candidats_par_region,
                   'nb_sieges_total': nb_sieges_total})


def bulletin_cass_tit(request):
    nb_sieges, candidats_par_region = get_donnees_bulletin_cass_tit()
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[consts.ELEC_CASS_TIT]
    return render(request, 'elections/bulletin/cass_tit.html',
                  {'nom_election': nom_election,
                   'nb_sieges': nb_sieges,
                   'regions': candidats_par_region})


def bulletin_autres(request, code_election):
    if code_election not in [consts.ELEC_CASS_ASS, consts.ELEC_PRES]:
        raise Http404()

    election = Election.objects.get(code=code_election)
    candidats = get_donnees_bulletin(election)
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[code_election]
    return render(request, 'elections/bulletin/autres.html',
                  {'nom_election': nom_election,
                   'nb_sieges': election.nb_sieges_global,
                   'candidats': candidats})


def depouillement_cells():
    return list(range(1, 21))


def depouillement_ca(request):
    candidats_par_region, nb_sieges_total = get_donnees_bulletin_ca()
    nb_sieges_total = sum(r['nb_sieges'] for r in candidats_par_region)
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[consts.ELEC_CA]
    return render(request, 'elections/depouillement/ca.html',
                  {'nom_election': nom_election,
                   'regions': candidats_par_region,
                   'nb_sieges_total': nb_sieges_total,
                   'cells': depouillement_cells(), })


def depouillement_cass_tit(request):
    nb_sieges_total, candidats_par_region = get_donnees_bulletin_cass_tit()
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[consts.ELEC_CASS_TIT]
    return render(request, 'elections/depouillement/cass_tit.html',
                  {'nom_election': nom_election,
                   'nb_sieges_total': nb_sieges_total,
                   'regions': candidats_par_region,
                   'cells': depouillement_cells(), })


def depouillement_autres(request, code_election):
    if code_election not in [consts.ELEC_CASS_ASS, consts.ELEC_PRES]:
        raise Http404()

    election = Election.objects.get(code=code_election)
    candidats = get_donnees_bulletin(election)
    nom_election = NOMS_ELECTIONS_LISTES_CANDIDATS[code_election]
    return render(request, 'elections/depouillement/autres.html',
                  {'nom_election': nom_election,
                   'nb_sieges_total': election.nb_sieges_global,
                   'candidats': candidats,
                   'cells': depouillement_cells(), })


def link_candidatures(critere_candidature):
    text = "Formulaire candidatures - {}".format(critere_candidature.titre)
    return {'url': reverse('candidatures_region',
                           args=(critere_candidature.code, )),
            'text': text}


def link_liste_candidats(critere_liste_candidats):
    return {'url': reverse('liste_candidats',
                           args=(critere_liste_candidats.code, )),
            'text': critere_liste_candidats.titre}


def accueil_elections(request):
    criteres_candidatures = get_candidatures_criteria()
    elections = list(Election.objects.exclude(code=consts.ELEC_CASS_RES))
    regions = [{'code': code, 'nom': nom}
               for code, nom in consts.REGIONS_VOTANTS]
    criteria_listes_votants = list(get_electeur_criteria().values())
    criteria_listes_candidats = list(get_all_listes_candidat_criteria(elections).values())
    par_categorie = []
    categories = CATEGORIES_ELECTIONS
    for categorie in categories:
        liens_criteres_categories = []
        for i, critere in reversed(list(enumerate(criteres_candidatures.values()))):
            if critere.categorie == categorie:
                liens_criteres_categories.append(link_candidatures(critere))
        for i, critere in reversed(list(enumerate(criteria_listes_candidats))):
            if critere.categorie == categorie:
                liens_criteres_categories.append(link_liste_candidats(critere))
        par_categorie.append((categorie[1], liens_criteres_categories))

    critere_candidatures_tous = criteres_candidatures[CRITERE_TOUS]
    return render(request, 'elections/accueil.html', {
        'regions': regions,
        'elections': elections,
        'criteria_listes_votants': criteria_listes_votants,
        'par_categorie': par_categorie,
        'critere_candidatures_tous': critere_candidatures_tous,
    })
