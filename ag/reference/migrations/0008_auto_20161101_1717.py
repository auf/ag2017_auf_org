# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0007_implantation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='implantation',
            options={'ordering': ('nom_court',)},
        ),
    ]
