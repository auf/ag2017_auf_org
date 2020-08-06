# -*- encoding: utf-8 -*

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from ag.inscription.views import (
    connexion_inscription,
    paypal_return,
    paypal_ipn,
    paypal_cancel,
    calcul_frais_programmation,
    make_paypal_invoice,
    processus_inscription,
)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='inscription/index.html'),
        name='info_inscription'),
    url(r'^conditions-generales/$', TemplateView.as_view(
        template_name='inscription/conditions_generales.html'),
        name='conditions_generales'),
    url(r'^connexion/(\w+)$', connexion_inscription,
        name='connexion_inscription'),
    url(r'^retour_paypal/$', paypal_return, name='paypal_return'),
    url(r'^notification_ipn_paypal/$', paypal_ipn, name='paypal_ipn'),
    url(r'^annulation_paypal/([-\w]+)$', paypal_cancel, name='paypal_cancel'),
    url(r'^inscriptions_terminees/$',
        TemplateView.as_view(template_name='inscription/terminees.html'),
        name='inscriptions_terminees'),
    url(r'^calcul_frais_programmation/$', calcul_frais_programmation,
        name='calcul_frais_programmation'),
    url(r'^make_paypal_invoice/$', make_paypal_invoice,
        name='make_paypal_invoice'),
    url(r'^(?P<url_title>[-\w]+)/$', processus_inscription,
        name='processus_inscription'),
]
