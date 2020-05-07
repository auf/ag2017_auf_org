# -*- encoding: utf-8 -*-
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from auf_django_mailing.models import ModeleCourriel, envoyer


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--limit',
            action='store',
            dest='limit',
            default=None,
            help=u"Nombre max. de courriels à envoyer"),
        )

    def handle(self, *args, **options):
        limit = options['limit']
        limit = limit if not limit else int(limit)

        codes = [values[0] for values in
                 ModeleCourriel.objects.all().values_list('code')]
        for code in codes:
            envoyer(code, settings.AG_INSCRIPTION_SENDER,
                    url_name='connexion_inscription', limit=limit)
