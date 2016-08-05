# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0002_auto_20160803_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitationenveloppe',
            name='enveloppe',
            field=models.OneToOneField(to='mailing.Enveloppe'),
        ),
    ]
