# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0004_auto_20160907_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalinvoice',
            name='inscription',
            field=models.ForeignKey(default=1, to='inscription.Inscription'),
            preserve_default=False,
        ),
    ]
