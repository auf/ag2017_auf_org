# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0004_region_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='etablissement',
            name='responsable_fonction',
            field=models.CharField(max_length=255, verbose_name='fonction', blank=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='responsable_genre',
            field=models.CharField(max_length=1, verbose_name='genre', blank=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='responsable_nom',
            field=models.CharField(max_length=255, verbose_name='nom', blank=True),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='responsable_prenom',
            field=models.CharField(max_length=255, verbose_name='pr\xe9nom', blank=True),
        ),
    ]
