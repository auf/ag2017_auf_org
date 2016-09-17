# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import dossier

urlpatterns = patterns(
    'ag.dossier_inscription.views',
    url(r'^dossier/$', dossier, name='dossier_inscription'),
)
