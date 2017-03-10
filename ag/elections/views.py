# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect

import ag.gestion.models as gestion_models
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        request.POST or None,
    )
    if request.method == 'POST':
        if candidatures_formset.is_valid():
            candidatures_formset = CandidatureFormset()
            print('valid!')
        return render(request, "elections/candidatures_form.html",
                      {'formset': candidatures_formset})
    else:
        return render(request, "elections/candidatures.html",
                      {'formset': candidatures_formset})
