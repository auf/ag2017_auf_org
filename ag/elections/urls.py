# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from ag.elections.views import liste_votants, SALLE, EMARGEMENT
from .views import candidatures

urlpatterns = patterns(
    'ag.elections.views',
    url(r'^$', TemplateView.as_view(template_name="elections/accueil.html"),
        name='accueil_elections'),
    url(r'^candidatures/$', candidatures, name='candidatures'),
    url(r'^liste_salle/([_\w]+)/$', liste_votants, name='liste_salle',
        kwargs={'salle_ou_emargement': SALLE}),
    url(r'^liste_emargement/([_\w]+)/$', liste_votants, name='liste_emargement',
        kwargs={'salle_ou_emargement': EMARGEMENT}),
)
