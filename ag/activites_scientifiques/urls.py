# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    'ag.activites_scientifiques.views',
    url(r'^$', 'pick', name='act_sci_pick'),
    url(r'^login/$', 'login', name='act_sci_login'),
    url(r'^logout/$', 'logout', name='act_sci_logout'),
    url(r'^clear/$', 'clear', name='act_sci_clear'),
    url(r'^not_found/$', TemplateView.as_view(
        template_name='activites_scientifiques/not_found.html'),
        name='act_sci_login_not_found'),
    url(r'^test/$', TemplateView.as_view(
        template_name='activites_scientifiques/test_container.html')),
)


