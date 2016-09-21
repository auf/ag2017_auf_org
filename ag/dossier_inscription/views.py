# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from ag.dossier_inscription import forms
from ag.dossier_inscription.models import InscriptionFermee, Adresse


def dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    adresse = inscription.get_adresse()
    context = {
        'inscription': inscription,
        'adresse': adresse,
        'suivi': inscription.get_suivi_dossier(),
        'solde': inscription.get_total_du(),
        'form_adresse': forms.AdresseForm(initial=adresse._asdict())
    }
    return render(request, 'dossier_inscription/dossier.html', context)


@require_POST
def set_adresse(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    form_adresse = forms.AdresseForm(request.POST)
    if form_adresse.is_valid():
        inscription.set_adresse(Adresse(**form_adresse.cleaned_data))
        inscription.save()
    return render(request, 'dossier_inscription/includes/adresse.html',
                  {'adresse': inscription.get_adresse(),
                   'form_adresse': form_adresse})
