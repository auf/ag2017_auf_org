# -*- encoding: utf-8 -*-
import sys
from ag.inscription.models import Invitation, InvitationEnveloppe
from ag.reference.models import Etablissement
from django.core.management.base import BaseCommand, CommandError
from auf_django_mailing.models import Enveloppe, ModeleCourriel


def creer_invitation_enveloppe_mandate(modele_courriel, etablissement):
        enveloppe = Enveloppe()
        enveloppe.modele = modele_courriel
        enveloppe.save()
        invitation = Invitation()
        invitation.etablissement = etablissement
        invitation.pour_mandate = True
        invitation.save()
        invitation_enveloppe = InvitationEnveloppe()
        invitation_enveloppe.invitation = invitation
        invitation_enveloppe.enveloppe = enveloppe
        invitation_enveloppe.save()


def get_etablissements_sans_invitation(modele_courriel):
    etablissements = Etablissement.objects \
        .exclude(responsable_courriel="") \
        .filter(membre=True) \
        .exclude(invitation__invitationenveloppe__enveloppe__modele=
                 modele_courriel)
    return etablissements


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            modele_courriel = ModeleCourriel.objects.get(code="mand")
        except ModeleCourriel.DoesNotExist:
            raise CommandError(
                "Il est nécessaire de créer un modèle de courriel avec"
                "le code 'mand' pour lancer la génération des invitations.")

        etablissements = get_etablissements_sans_invitation(modele_courriel)
        for etablissement in etablissements:
            creer_invitation_enveloppe_mandate(modele_courriel, etablissement)

