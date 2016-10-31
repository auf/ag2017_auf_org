# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0006_region_adresse'),
    ]

    operations = [
        migrations.CreateModel(
            name='Implantation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('nom_court', models.CharField(max_length=255, blank=True)),
            ],
        ),
    ]
