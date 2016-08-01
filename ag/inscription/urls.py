# -*- encoding: utf-8 -*

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    'ag.inscription.views',
    url(r'^$', TemplateView.as_view(template_name='inscription/index.html'), name='info_inscription'),
    url(r'^conditions-generales/$', TemplateView.as_view(template_name='inscription/conditions_generales.html'), name='conditions_generales'),
    url(r'^connexion/(\w+)$', 'connexion_inscription', name='connexion_inscription'),
    url(r'^ajout_invitations/$', 'ajout_invitations', name='ajout_invitations'),
    url(r'^retour_paypal/(\d+)/$', 'paypal_return', name='paypal_return'),
    url(r'^notification_ipn_paypal/$', 'paypal_ipn', name='paypal_ipn'),
    url(r'^annulation_paypal/$', 'paypal_cancel', name='paypal_cancel'),
    url(r'^inscriptions_terminees/$', TemplateView.as_view(template_name='inscription/terminees.html'), name='inscriptions_terminees'),
    url(r'^(?P<url_title>[-\w]+)/$', 'processus_inscription', name='processus_inscription'),
)
