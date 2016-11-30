# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0001_initial'),
        ('gestion', '0003_auto_20161117_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorieFonction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
            ],
            options={
                'verbose_name': 'Cat\xe9gorie fonction participant',
                'verbose_name_plural': 'Cat\xe9gories fonctions participants',
            },
        ),
        migrations.CreateModel(
            name='Fonction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('ordre', models.IntegerField()),
                ('categorie', models.ForeignKey(to='gestion.CategorieFonction')),
            ],
            options={
                'ordering': ['ordre'],
                'verbose_name': 'Fonction participant',
                'verbose_name_plural': 'Fonctions participants',
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=512)),
                ('pays', models.ForeignKey(to='reference.Pays')),
                ('region', models.ForeignKey(to='reference.Region')),
            ],
        ),
        migrations.CreateModel(
            name='TypeInstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('ordre', models.IntegerField()),
            ],
            options={
                'ordering': ['ordre'],
                'verbose_name': "Type d'institution",
                'verbose_name_plural': "Types d'institutions",
            },
        ),
        migrations.RemoveField(
            model_name='participant',
            name='statut',
        ),
        migrations.AddField(
            model_name='participant',
            name='membre_ca_represente',
            field=models.CharField(blank=True, max_length=1, null=True, verbose_name='Ce membre du CA repr\xe9sente', choices=[(b'E', '\xc9tablissement'), (b'G', 'Gouvernement')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='instance_auf',
            field=models.CharField(blank=True, max_length=1, null=True, verbose_name="Instance de l'AUF", choices=[(b'A', "Conseil d'administration"), (b'S', 'Conseil scientifique')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='modalite_retrait_billet',
            field=models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de retrait du billet', choices=[('0', 'Vos billets vous seront transmis par votre bureau r\xe9gional'), ('1', 'Vos billets seront disponibles au comptoir de la compagnie a\xe9rienne'), ('3', "Vos billets de train et d'avion vous seront transmis par votre bureau r\xe9gional"), ('4', "Vos billets de train et d'avion seront disponibles aux comptoirs de la compagnie a\xe9rienne et de la SNCF")]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='modalite_versement_frais_sejour',
            field=models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de versement', choices=[(b'A', '\xc0 votre arriv\xe9e \xe0 Marrakech'), (b'I', 'Par le bureau r\xe9gional')]),
        ),
        migrations.AddField(
            model_name='institution',
            name='type_institution',
            field=models.ForeignKey(to='gestion.TypeInstitution'),
        ),
        migrations.AddField(
            model_name='fonction',
            name='type_institution',
            field=models.ForeignKey(blank=True, to='gestion.TypeInstitution', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='fonction',
            field=models.ForeignKey(blank=True, to='gestion.Fonction', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='institution',
            field=models.ForeignKey(blank=True, to='gestion.Institution', null=True),
        ),
    ]
