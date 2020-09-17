# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0012_participant_candidat_statut'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='candidat_elimine',
        ),
    ]
