# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import dossier, set_adresse

urlpatterns = patterns(
    'ag.dossier_inscription.views',
    url(r'^$', dossier, name='dossier_inscription'),
    url(r'^set_adresse/$', set_adresse, name='set_adresse'),
)
