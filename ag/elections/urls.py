# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from .views import candidatures

urlpatterns = patterns(
    'ag.elections.views',
    url(r'^$', TemplateView.as_view(template_name="elections/accueil.html"),
        name='accueil_elections'),
    url(r'^candidatures/$', candidatures, name='candidatures'),
)