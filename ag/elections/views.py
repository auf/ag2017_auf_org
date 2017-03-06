# -*- encoding: utf-8 -*-
from django.shortcuts import render

import ag.gestion.models as gestion_models
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        queryset=gestion_models.Participant.actifs
        .all().filter_representants_mandates()
        .avec_region_vote()
        .order_by('region_vote', 'nom', 'prenom'))
    return render(request, "elections/candidatures.html",
                  {'formset': candidatures_formset})
