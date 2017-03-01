# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import (
    vue_dossier,
    set_adresse,
    reseautage_on_off,
    upload_passeport,
    facture_dossier,
)

urlpatterns = patterns(
    'ag.dossier_inscription.views',
    url(r'^$', vue_dossier, name='dossier_inscription'),
    url(r'^set_adresse/$', set_adresse, name='set_adresse'),
    url(r'^upload_passeport/$', upload_passeport, name='upload_passeport'),
    url(r'^reseautage_on_off/$', reseautage_on_off, name='reseautage_on_off'),
    url(r'^facture/$', facture_dossier, name='facture_dossier'),
    url(r'^coupon_transport/$', 'coupon_transport_dossier',
        name='coupon_transport_dossier'),
)
