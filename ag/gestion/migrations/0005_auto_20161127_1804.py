# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_auto_20161125_1246'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StatutParticipant',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='nom_autre_institution',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='pays_autre_institution',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='type_autre_institution',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='type_institution',
        ),
        migrations.DeleteModel(
            name='TypeInstitutionSupplementaire',
        ),
    ]
