# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0011_auto_20170328_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='candidat_statut',
            field=models.CharField(default=b'dans_course', max_length=16, choices=[(b'dans_course', 'Dans la course'), (b'elu', '\xc9lu'), (b'elimine', '\xc9limin\xe9')]),
        ),
    ]
