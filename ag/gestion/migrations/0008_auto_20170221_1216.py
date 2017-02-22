# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import ag.gestion.models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_auto_20170109_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichier',
            name='fichier',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'/media/benselme/data/dev/auf/ag2017_auf_org/medias_participants'), upload_to=ag.gestion.models.get_participant_file_path),
        ),
        migrations.AlterField(
            model_name='participant',
            name='imputation',
            field=models.CharField(blank=True, max_length=32, choices=[(b'A0394DRI017B3', b'A0394DRI017B3'), (b'A0394DRI016A3', b'A0394DRI016A3')]),
        ),
    ]
