# -*- encoding: utf-8 -*-
from django.http.response import Http404
from django.shortcuts import render

from ag.elections.models import get_electeur_criteria, get_donnees_liste_salle, \
    get_all_listes_candidat_criteria, Election, filter_participants, \
    get_donnees_bulletin_ca, get_donnees_bulletin_cass_tit
from ag.gestion import consts
from ag.reference.models import Region
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        request.POST or None,
    )
    if request.method == 'POST':
        if candidatures_formset.is_valid():
            candidats = candidatures_formset.get_updated_candidats()
            candidats.update_participants()
            candidatures_formset = CandidatureFormset()
        return render(request, "elections/candidatures_form.html",
                      {'formset': candidatures_formset})
    else:
        return render(request, "elections/candidatures.html",
                      {'formset': candidatures_formset})


SALLE = 'salle'
EMARGEMENT = 'emargement'


def liste_votants(request, code_critere, salle_ou_emargement):
    criteria = get_electeur_criteria()
    critere = critere_or_404(code_critere, criteria)
    donnees = get_donnees_liste_salle(critere)
    template = u"elections/liste_{}/{}.html".format(
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
    consts.ELEC_PRES: u"Présidence",
    consts.ELEC_CA: u"Membres universitaires du Conseil d’administration et "
                    u"leur suppléants",
    consts.ELEC_CASS_TIT: u"Représentants des membres titulaires du Conseil "
                          u"associatif",
    consts.ELEC_CASS_ASS: u"Représentants des membres Associés du Conseil "
                          u"associatif",
    consts.ELEC_CASS_RES: u"Représentants des réseaux institutionnels du "
                          u"Conseil associatif",
}


def liste_candidats(request, code_critere):
    elections = Election.objects.all()
    criteria = get_all_listes_candidat_criteria(elections)
    critere = critere_or_404(code_critere, criteria)
    participants = filter_participants(critere.filter)
    participants = participants.order_by('nom', 'prenom', )\
        .select_related('etablissement')
    if critere.code_region:
        nom_region = Region.objects.get(code=critere.code_region).nom
    else:
        nom_region = u""
    return render(
        request,
        u"elections/liste_candidats/base.html",
        {
            'participants': participants,
            'titre_critere': critere.titre,
            'nom_election': NOMS_ELECTIONS_LISTES_CANDIDATS[
                critere.code_election],
            'nom_region': nom_region,
            'election_ca': critere.code_election == consts.ELEC_CA,
        })


def bulletin_ca(request):
    candidats_par_region = get_donnees_bulletin_ca()
    nb_sieges_total = sum(r['nb_sieges'] for r in candidats_par_region)
    return render(request, 'elections/bulletin/ca.html',
                  {'regions': candidats_par_region,
                   'nb_sieges_total': nb_sieges_total})


def bulletin_cass_tit(request):
    nb_sieges, candidats_par_region = get_donnees_bulletin_cass_tit()
    return render(request, 'elections/bulletin/cass_tit.html',
                  {'nb_sieges': nb_sieges,
                   'regions': candidats_par_region})


def bulletin(request, code_election):
    pass
