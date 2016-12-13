# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='etablissement',
            options={'ordering': ('nom',)},
        ),
        migrations.AlterModelOptions(
            name='pays',
            options={'ordering': ('nom',)},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'ordering': ('nom',)},
        ),
        migrations.AddField(
            model_name='implantation',
            name='region',
            field=models.ForeignKey(to='reference.Region', null=True),
        ),
    ]
