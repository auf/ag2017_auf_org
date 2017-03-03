# -*- encoding: utf-8 -*-
from django.shortcuts import render

import ag.gestion.models as gestion_models
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        queryset=gestion_models.Participant.actifs
        .all().filter_representants_mandates())
    return render(request, "elections/candidatures.html",
                  {'formset': candidatures_formset})
