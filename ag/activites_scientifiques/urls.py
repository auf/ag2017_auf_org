# -*- encoding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView
from ag.activites_scientifiques import views

urlpatterns = [
    url(r'^$', views.pick, name='act_sci_pick'),
    url(r'^login/$', views.login, name='act_sci_login'),
    url(r'^logout/$', views.logout, name='act_sci_logout'),
    url(r'^clear/$', views.clear, name='act_sci_clear'),
    url(r'^not_found/$', TemplateView.as_view(
        template_name='activites_scientifiques/not_found.html'),
        name='act_sci_login_not_found'),
    url(r'^test/$', TemplateView.as_view(
        template_name='activites_scientifiques/test_container.html')),
]


