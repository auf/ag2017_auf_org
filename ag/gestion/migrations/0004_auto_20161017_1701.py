# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0003_auto_20160915_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichier',
            name='type_fichier',
            field=models.IntegerField(default=0, choices=[(0, 'Autres'), (1, 'Passeport')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='paiement',
            field=models.CharField(blank=True, max_length=2, verbose_name='modalit\xe9s de paiement', choices=[(b'CB', 'Carte bancaire'), (b'VB', 'Virement bancaire'), (b'CE', 'Ch\xe8que en euros'), (b'DL', 'Devises locales')]),
        ),
    ]
