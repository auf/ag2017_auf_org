# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0018_forfait'),
        ('gestion', '0005_auto_20161024_1802'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='accompte',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='accompte_devise_locale',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='montant_accompte_devise_locale',
        ),
        migrations.AddField(
            model_name='activite',
            name='forfait_invite',
            field=models.ForeignKey(verbose_name='Forfait invit\xe9 correspondant', blank=True, to='inscription.Forfait', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='forfaits',
            field=models.ManyToManyField(to='inscription.Forfait'),
        ),
    ]
