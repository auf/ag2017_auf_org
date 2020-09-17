# -*- encoding: utf-8 -*-
from auf_django_mailing.models import Enveloppe, ModeleCourriel
from ag.inscription.models import Invitation, InvitationEnveloppe
from ag.reference.models import Etablissement
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--destinataires',
            action='store',
            dest='destinataires',
            default=False,
            help="Destinataires: `mandates` ou `invites`"
        )

    def handle(self, *args, **options):
        destinataires = options['destinataires']
        if destinataires == 'mandates':
            code_modele_initial = 'mand'
            code_modele_rappel = 'mand_rel'
        elif destinataires == 'invites':
            code_modele_initial = 'acc'
            code_modele_rappel = 'acc_rel'
        else:
            raise CommandError("Precisez si le rappel est destine aux"
                "mandates ou aux invites")

        modele_rappel = ModeleCourriel.objects.get(code=code_modele_rappel)
        # on cherche les invitations qui n'ont pas débouché sur une
        # inscription complétée et qui correspondent soit aux mandatés
        # soit aux invités
        invitations = Invitation.objects.filter(
            Q(inscription__id__isnull=True)
            | Q(inscription__fermee=False),
            invitationenveloppe__enveloppe__modele__code=code_modele_initial,
            etablissement__in=Etablissement.objects.exclude(participant__id__isnull=False))
        for invitation in invitations:
            enveloppe = Enveloppe()
            enveloppe.modele = modele_rappel
            enveloppe.save()
            invitation_enveloppe = InvitationEnveloppe()
            invitation_enveloppe.enveloppe = enveloppe
            invitation_enveloppe.invitation = invitation
            invitation_enveloppe.save()



