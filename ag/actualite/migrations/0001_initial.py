# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actualite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titre', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('texte', models.TextField()),
                ('image', models.ImageField(null=True, upload_to=b'actualite', blank=True)),
                ('date_pub', models.DateField()),
                ('date_mod', models.DateTimeField(auto_now_add=True, verbose_name=b'date de derniere modification')),
                ('status', models.CharField(default=b'3', max_length=1, choices=[(b'1', b'En cours de redaction'), (b'2', b'Propose a la publication'), (b'3', b'Publie en Ligne'), (b'4', b'A supprimer')])),
            ],
            options={
                'ordering': ('-date_pub',),
            },
        ),
    ]
