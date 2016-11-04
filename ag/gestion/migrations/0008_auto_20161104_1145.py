# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_remove_activite_prix_invite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='facturation_supplement_chambre_double',
        ),
        migrations.AlterField(
            model_name='participant',
            name='nationalite',
            field=models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nationalit\xc3\xa9', blank=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='nom',
            field=models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nom'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='prenom',
            field=models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'pr\xc3\xa9nom(s)'),
        ),
    ]
