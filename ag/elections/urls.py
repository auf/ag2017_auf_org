# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from ag.elections.views import (
    liste_votants, SALLE, EMARGEMENT, liste_candidats, bulletin_autres,
    bulletin_ca, bulletin_cass_tit, depouillement_ca, depouillement_cass_tit,
    depouillement_autres, accueil_elections)
from .views import candidatures


urlpatterns = patterns(
    'ag.elections.views',
    url(r'^$', accueil_elections,
        name='accueil_elections'),
    url(r'^candidatures/$', candidatures, name='candidatures'),
    url(r'^candidatures/(\w+)/$', candidatures, name='candidatures_region'),
    url(r'^liste_salle/([_\w]+)/$', liste_votants, name='liste_salle',
        kwargs={'salle_ou_emargement': SALLE}),
    url(r'^liste_emargement/([_\w]+)/$', liste_votants, name='liste_emargement',
        kwargs={'salle_ou_emargement': EMARGEMENT}),
    url(r'^liste_candidats/([_\-\w]+)/$', liste_candidats,
        name='liste_candidats'),
    url(r'^bulletin/ca/$', bulletin_ca, name='bulletin_ca'),
    url(r'^bulletin/cass-tit/$', bulletin_cass_tit,
        name='bulletin_cass_tit'),
    url(r'^bulletin/([_\-\w]+)/$', bulletin_autres, name='bulletin_autres'),
    url(r'^grille_depouillement/ca/$', depouillement_ca,
        name='depouillement_ca'),
    url(r'^grille_depouillement/cass-tit/$', depouillement_cass_tit,
        name='depouillement_cass_tit'),
    url(r'^grille_depouillement/([_\-\w]+)/$', depouillement_autres,
        name='depouillement_autres'),
)
