# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from auf_django_mailing.models import ModeleCourriel, envoyer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            action='store',
            dest='limit',
            default=None,
            help="Nombre max. de courriels à envoyer"
        )

    def handle(self, *args, **options):
        limit = options['limit']
        limit = limit if not limit else int(limit)

        codes = [values[0] for values in
                 ModeleCourriel.objects.all().values_list('code')]
        for code in codes:
            envoyer(code, settings.AG_INSCRIPTION_SENDER,
                    url_name='connexion_inscription', limit=limit)
