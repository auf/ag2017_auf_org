# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0002_auto_20160805_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='inscription',
            field=models.OneToOneField(null=True, to='inscription.Inscription'),
        ),
    ]
