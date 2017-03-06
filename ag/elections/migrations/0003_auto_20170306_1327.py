# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_auto_20170306_1325'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='election',
            options={'ordering': ['ordre']},
        ),
    ]
