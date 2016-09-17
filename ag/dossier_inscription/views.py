# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect
from ag.dossier_inscription.models import InscriptionFermee


def dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    context = {
        'inscription': inscription,
        'adresse': inscription.get_adresse(),
    }
    return render('dossier_inscription/dossier.html', context)
