# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0017_remove_inscription_paiement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forfait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('montant', models.IntegerField()),
                ('categorie', models.CharField(max_length=4, choices=[(b'insc', 'Inscription'), (b'invi', 'Invit\xe9'), (b'hebe', 'H\xe9bergement')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
