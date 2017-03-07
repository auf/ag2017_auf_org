# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect

import ag.gestion.models as gestion_models
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        request.POST or None,
        queryset=gestion_models.Participant.actifs
        .all().filter_representants_mandates()
        .avec_region_vote()
        .order_by('region_vote', 'nom', 'prenom'))
    if request.method == 'POST' and candidatures_formset.is_valid():
        candidatures_formset.save()
        # redirect pour recharger la liste des suppléants
        return redirect('candidatures')
    else:
        return render(request, "elections/candidatures.html",
                      {'formset': candidatures_formset})
