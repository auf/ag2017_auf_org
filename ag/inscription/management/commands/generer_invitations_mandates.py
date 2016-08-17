# -*- encoding: utf-8 -*-
import sys
from ag.inscription.models import Invitation, InvitationEnveloppe
from ag.reference.models import Etablissement
from django.core.management.base import BaseCommand, CommandError
from auf.django.mailing.models import Enveloppe, ModeleCourriel


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            modele_courriel = ModeleCourriel.objects.get(code="mand")
        except ModeleCourriel.DoesNotExist:
            raise CommandError(
                u"Il est nécessaire de créer un modèle de courriel avec"
                u"le code 'mand' pour lancer la génération des invitations.")

        etablissements = Etablissement.objects.exclude(responsable_courriel="")\
            .filter(membre=True)\
            .exclude(invitation__invitationenveloppe__enveloppe__modele=modele_courriel)
            #.exclude(id__in=[627,125,138,403,643,890,642,921,226])\
        for etablissement in etablissements:
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
