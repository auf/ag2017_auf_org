# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0009_auto_20170302_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='suppleant_de',
            field=models.OneToOneField(related_name='suppleant', null=True, blank=True, to='gestion.Participant'),
        ),
    ]
