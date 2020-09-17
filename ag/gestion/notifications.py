# -*- encoding: utf-8 -*-
import sys

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.template import Template, Context
from auf_django_mailing.models import ModeleCourriel
from django.conf import settings
from ag.gestion.transfert_inscription import inscription_transferee
from ag.inscription.templatetags.inscription import adresse_email_region
from ag.inscription.views import inscription_confirmee
from ag.gestion.models import facturation_validee, nouveau_participant
from ag.inscription.models import paypal_signal

from django.core.mail import EmailMessage


def format_url(path):
    domain = Site.objects.get(pk=1).domain
    return "https://{0}{1}".format(domain, path)


def url_participant(participant):
    path = reverse('fiche_participant', args=(participant.id,))
    return format_url(path)


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
        print(sys.exc_info())
        raise


@receiver(paypal_signal)
def paypal_handler(sender, **kwargs):
    body = "Un paiement paypal a été effectué pour l'inscription"\
           " numéro {} au nom de {} de l'établissement {}".format(
               sender.inscription.numero, sender.get_nom_prenom(),
               sender.inscription.get_etablissement().nom)
    if sender.montant and sender.devise:
        body += " Montant: " + sender.montant + sender.devise
    if sender.statut:
        body += ", Statut:" + sender.statut

    envoyer_a_service('finance', 'Paiement paypal reçu', body)


@receiver(facturation_validee)
def facturation_validee_handler(sender, **kwargs):
    objet, body = get_nouveau_participant_mail(sender)
    subject = "Facturation validée : %s" % objet
    envoyer_a_service('finance', subject, body)
    envoyer_a_service('service_institutions', subject, body)
    envoyer_a_service('bureau_missions', subject, body)


def get_nouveau_participant_mail(participant):
    region = participant.get_region().nom if participant.get_region() else "Région?"
    etablissement = participant.etablissement.nom if participant.etablissement else "Établissement?"
    fonction = participant.fonction.libelle if participant.fonction else \
        "Fonction?"
    subject = "AG2017 Nouveau participant - " + region + "-" + fonction +\
              "-" + etablissement
    # todo: rétablir paiement dans mail transfert
    # body = participant.get_paiement_display() + u"-"
    body = "Prise en charge transport:" +\
            participant.get_prise_en_charge_transport_text() + "-"
    body += "Prise en charge hébergement:" +\
            participant.get_prise_en_charge_sejour_text() + "-"
    body += " " + format_url(
        reverse('fiche_participant', args=(participant.id,)))
    return subject, body


@receiver(nouveau_participant)
def nouveau_participant_handler(sender, **kwargs):
    body = "Le participant " + sender.get_nom_prenom()\
           + " a été créé " + url_participant(sender)
    subject, body = get_nouveau_participant_mail(sender)
    envoyer_a_service('gestion', subject, body)


def send_courriel_inscrit(modele_code, inscription):
    modele_courriel = ModeleCourriel.objects.get(code=modele_code)
    message = EmailMessage()
    message.subject = modele_courriel.sujet
    modele_corps = Template(modele_courriel.corps)
    context = inscription.invitation.get_courriel_template_context()
    message.body = modele_corps.render(Context(context))
    if hasattr(settings, 'MAILING_TEST_ADDRESS'):
        message.to = [settings.MAILING_TEST_ADDRESS, ]
    else:
        message.to = [inscription.courriel, ]
    message.from_email = settings.GESTION_AG_SENDER
    message.content_subtype = "html" if modele_courriel.html else "text"
    message.send(fail_silently=True)


@receiver(inscription_confirmee)
def inscription_confirmee_handler(sender, **kwargs):
    send_courriel_inscrit("recu_ok", sender)

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
    region = sender.get_etablissement().region
    nom_region = region.nom
    type_inscription = "mandaté" if sender.est_pour_mandate() \
        else "accompagnateur"

    subject = "ag2017 nouvelle inscription web " + nom_region + "-" +\
              type_inscription + "-" + sender.get_etablissement().nom
    body = "" + format_url(
        reverse('admin:gestion_inscriptionweb_change', args=(sender.id,)))
    envoyer_a_service('inscription', subject, body)

    message = EmailMessage()
    message.subject = subject
    message.body = body
    message.to = [adresse_email_region(region.code)]
    message.from_email = settings.GESTION_AG_SENDER
    message.send(fail_silently=True)
