# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import dossier, set_adresse, reseautage_on_off

urlpatterns = patterns(
    'ag.dossier_inscription.views',
    url(r'^$', dossier, name='dossier_inscription'),
    url(r'^set_adresse/$', set_adresse, name='set_adresse'),
    url(r'^reseautage_on_off/$', reseautage_on_off, name='reseautage_on_off'),
)
