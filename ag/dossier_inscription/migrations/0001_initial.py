# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionFermee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('inscription.inscription',),
        ),
    ]
