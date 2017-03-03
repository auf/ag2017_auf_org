# -*- encoding: utf-8 -*-
import ag.gestion.models as gestion_models
from .forms import CandidatureFormset


def candidatures(request):
    candidatures_formset = CandidatureFormset(
        queryset=gestion_models.Participant.actifs
            .filter_representants_mandates())
