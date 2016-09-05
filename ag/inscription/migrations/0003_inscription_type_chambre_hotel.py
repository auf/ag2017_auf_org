# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0002_auto_20160902_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='type_chambre_hotel',
            field=models.CharField(default='1', max_length=1, choices=[(b'1', b'chambre avec 1 lit simple'), (b'2', b'chambre double (suppl\xc3\xa9ment de 100\xe2\x82\xac)')]),
            preserve_default=False,
        ),
    ]
