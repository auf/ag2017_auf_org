# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participationactivite',
            name='avec_invites',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='statutparticipant',
            name='droit_de_vote',
            field=models.BooleanField(default=False),
        ),
    ]
