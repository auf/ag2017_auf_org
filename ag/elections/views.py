# -*- encoding: utf-8 -*-
from django.http.response import Http404
from django.shortcuts import render

from ag.elections.models import get_electeur_criteria, get_donnees_liste_salle
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
    try:
        critere = criteria[code_critere]
    except KeyError:
        raise Http404()
    donnees = get_donnees_liste_salle(critere)
    template = u"elections/liste_{}/{}.html".format(
        salle_ou_emargement, critere.code)
    return render(request, template, {
        'participants_par_pays': donnees,
        'titre_critere': critere.titre,
    })
