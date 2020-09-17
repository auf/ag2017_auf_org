# -*- encoding: utf-8 -*-
from auf.django.mailing.models import EntreeLog
from django.db import connection
from django.core.management.base import BaseCommand

from ag.inscription.models import Invitation

SQL = """SELECT
  e.id AS etablissement_id
FROM (((reference_etablissement e
  INNER JOIN inscription_invitation inv ON inv.etablissement_id = e.id)
  INNER JOIN inscription_invitationenveloppe ie ON ie.invitation_id = inv.id)
  INNER JOIN mailing_enveloppe env ON env.id = ie.enveloppe_id)
  INNER JOIN mailing_entreelog log ON log.enveloppe_id = env.id
WHERE log.adresse <> e.responsable_courriel
AND NOT EXISTS(SELECT 1 FROM mailing_entreelog
               WHERE mailing_entreelog.adresse = e.responsable_courriel)
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute(SQL)
        # les ids de tous les établissements dont l'adresse de courriel a
        # changé depuis le dernier envoi
        etablissement_ids = [row[0] for row in cursor.fetchall()]
        invitations = Invitation.objects.filter(
            etablissement_id__in=etablissement_ids)
        for invitation in invitations:
            enveloppes = [ie.enveloppe
                          for ie in invitation.invitationenveloppe_set.all()]
            for entree in EntreeLog.objects.filter(enveloppe__in=enveloppes):
                print(("{0} -> {1}".format(entree.adresse,
                                           entree.enveloppe.get_adresse())))
                entree.adresse = entree.enveloppe.get_adresse()
                entree.save(update_fields=['adresse'])
