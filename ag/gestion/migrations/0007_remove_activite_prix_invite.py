# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_auto_20161101_1717'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activite',
            name='prix_invite',
        ),
    ]
