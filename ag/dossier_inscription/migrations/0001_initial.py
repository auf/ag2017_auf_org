# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0017_remove_inscription_paiement'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionFermee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('inscription.inscription',),
        ),
    ]
