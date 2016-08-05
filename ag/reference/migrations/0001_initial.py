# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Etablissement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('adresse', models.CharField(max_length=255, blank=True)),
                ('code_postal', models.CharField(max_length=20, verbose_name='code postal', blank=True)),
                ('ville', models.CharField(max_length=255, blank=True)),
                ('telephone', models.CharField(max_length=255, verbose_name='t\xe9l\xe9phone', blank=True)),
                ('fax', models.CharField(max_length=255, blank=True)),
                ('responsable_courriel', models.EmailField(max_length=254, verbose_name='courriel', blank=True)),
                ('statut', models.CharField(blank=True, max_length=1, null=True, choices=[(b'T', b'Titulaire'), (b'A', b'Associ\xc3\xa9'), (b'C', b'Candidat')])),
                ('qualite', models.CharField(blank=True, max_length=3, null=True, verbose_name='qualit\xe9', choices=[(b'ESR', b"\xc3\x89tablissement d'enseignement sup\xc3\xa9rieur et de recherche"), (b'CIR', b'Centre ou institution de recherche'), (b'RES', b'R\xc3\xa9seau')])),
            ],
        ),
        migrations.CreateModel(
            name='Pays',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('sud', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='etablissement',
            name='pays',
            field=models.ForeignKey(to='reference.Pays'),
        ),
        migrations.AddField(
            model_name='etablissement',
            name='region',
            field=models.ForeignKey(verbose_name=b'r\xc3\xa9gion', blank=True, to='reference.Region', null=True),
        ),
    ]
