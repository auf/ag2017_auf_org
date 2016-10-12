# -*- encoding: utf-8 -*-
import sys
from ag import settings
from ag.gestion.transfert_inscription import inscription_transferee
from ag.inscription.views import inscription_confirmee
from auf.django.mailing.models import ModeleCourriel
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from django.db.models.signals import post_save
from django.dispatch import receiver
from ag.gestion.models import Participant, facturation_validee, nouveau_participant
from ag.inscription.models import paypal_signal

from django.core.mail import EmailMessage

def format_url(path):
    domain = Site.objects.get(pk=1).domain
    return "https://{0}{1}".format(domain, path)


def url_participant(participant):
    path = reverse('fiche_participant', args=(participant.id,))
    return format_url(path)


def envoyer_a_participant(participant, subject, body):
    if participant.courriel:
        message = EmailMessage()
        message.subject = subject
        message.body = body
        message.to = [participant.courriel]
        message.from_email = settings.GESTION_AG_SENDER
        message.send(fail_silently=True)


def envoyer_a_service(code_service, subject, body):
    """ code_service correspond à une clé du setting DESTINATAIRES_NOTIFICATIONS
    """
    destinataires = settings.DESTINATAIRES_NOTIFICATIONS.get(code_service, None)
    if destinataires:
        message = EmailMessage()
        message.subject = subject
        message.body = body
        message.to = settings.DESTINATAIRES_NOTIFICATIONS[code_service]
        message.from_email = settings.GESTION_AG_SENDER
        message.send(fail_silently=True)


def envoyer_a_bureau_regional(participant, subject, body):
    adresse_bureau = participant.get_region().implantation_bureau.courriel_interne
    if adresse_bureau:
        message = EmailMessage()
        message.subject = subject
        message.body = body
        message.to = adresse_bureau
        message.from_email = settings.GESTION_AG_SENDER
        message.send(fail_silently=True)


@receiver(inscription_transferee)
def transfert_handler(sender, **kwargs):
    try:
        subject, body = get_nouveau_participant_mail(sender)
        envoyer_a_service('service_institutions', subject, body)
    except:
        print sys.exc_info()
        raise


@receiver(paypal_signal)
def paypal_handler(sender, **kwargs):
    body = u"Un paiement paypal a été effectué pour l'inscription"\
           u" numéro {} au nom de {} de l'établissement {}".format(
               sender.inscription.numero, sender.get_nom_prenom(),
               sender.inscription.get_etablissement().nom)
    if sender.montant and sender.devise:
        body += u" Montant: " + sender.montant + sender.devise
    if sender.statut:
        body += u", Statut:" + sender.statut

    envoyer_a_service('finance', 'Paiement paypal reçu', body)


@receiver(facturation_validee)
def facturation_validee_handler(sender, **kwargs):
    objet, body = get_nouveau_participant_mail(sender)
    subject = u"Facturation validée : %s" % objet
    envoyer_a_service('finance', subject, body)
    envoyer_a_service('service_institutions', subject, body)
    envoyer_a_service('bureau_missions', subject, body)


def get_nouveau_participant_mail(participant):
    region = participant.get_region().nom if participant.get_region() else u"Région?"
    etablissement = participant.etablissement.nom if participant.etablissement else u"Établissement?"
    statut = participant.statut.libelle if participant.statut else u"Statut?"
    subject = u"AG2013 Nouveau participant - " + region + u"-" + statut + u"-"\
              + etablissement
    body = participant.get_paiement_display() + u"-"
    body += u"Prise en charge transport:" +\
            participant.get_prise_en_charge_transport_text() + u"-"
    body += u"Prise en charge hébergement:" +\
            participant.get_prise_en_charge_sejour_text() + u"-"
    body += u" " + format_url(
        reverse('fiche_participant', args=(participant.id,)))
    return subject, body


@receiver(nouveau_participant)
def nouveau_participant_handler(sender, **kwargs):
    body = u"Le participant " + sender.get_nom_prenom()\
           + u" a été créé " + url_participant(sender)
    subject, body = get_nouveau_participant_mail(sender)
    envoyer_a_service('gestion', subject, body)


@receiver(inscription_confirmee)
def inscription_confirmee_handler(sender, **kwargs):
    modele_courriel = ModeleCourriel.objects.get(code="recu_ok")
    message = EmailMessage()
    message.subject = modele_courriel.sujet
    message.body = modele_courriel.corps
    if hasattr(settings, 'MAILING_TEST_ADDRESS'):
        message.to = [settings.MAILING_TEST_ADDRESS,]
    else:
        message.to = [sender.courriel, ]
    message.from_email = settings.GESTION_AG_SENDER
    message.content_subtype = "html" if modele_courriel.html else "text"
    message.send(fail_silently=True)

#    if sender.etablissement_delinquant():
#        modele_courriel = ModeleCourriel.objects.get(code="coti_rel")
#        message = EmailMessage()
#        message.subject = modele_courriel.sujet
#        message.body = modele_courriel.corps
#        if hasattr(settings, 'MAILING_TEST_ADDRESS'):
#            message.to = [settings.MAILING_TEST_ADDRESS,]
#        else:
#            message.to = [sender.courriel,]
#        message.from_email = settings.GESTION_AG_SENDER
#        message.content_subtype = "html" if modele_courriel.html else "text"
#        message.send(fail_silently=True)
#
    region = sender.get_etablissement().region.nom
    type_inscription = u"mandaté" if sender.est_pour_mandate()\
    else u"accompagnateur"

    subject = u"ag2013 nouvelle inscription web " + region + u"-" + type_inscription\
              + u"-" + sender.get_etablissement().nom
    body = u"" + format_url(
        reverse('admin:gestion_inscriptionweb_change', args=(sender.id,)))
    envoyer_a_service('inscription', subject, body)


