# -*- encoding: utf-8 -*-
from django.http.response import Http404
from django.shortcuts import render, redirect

import ag.gestion.models as gestion_models
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


def liste_salle(request, code_critere):

    criteria = get_electeur_criteria()
    try:
        critere = criteria[code_critere]
    except KeyError:
        raise Http404()
    donnees = get_donnees_liste_salle(critere)
    template = u"elections/liste_salle_{}.html".format(critere.code)
    return render(request, template, {'participants_par_pays': donnees})
