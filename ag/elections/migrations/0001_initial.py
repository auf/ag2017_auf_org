# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('nb_sieges_global', models.IntegerField(null=True, verbose_name='Global', blank=True)),
                ('nb_sieges_afrique', models.IntegerField(null=True, verbose_name='Afrique', blank=True)),
                ('nb_sieges_ameriques', models.IntegerField(null=True, verbose_name='Am\xe9riques', blank=True)),
                ('nb_sieges_asie_pacifique', models.IntegerField(null=True, verbose_name='Asie-Pacifique', blank=True)),
                ('nb_sieges_europe_ouest', models.IntegerField(null=True, verbose_name="Europe de l'ouest", blank=True)),
                ('nb_sieges_europe_est', models.IntegerField(null=True, verbose_name='Europe centrale et orientale', blank=True)),
                ('nb_sieges_maghreb', models.IntegerField(null=True, verbose_name='Maghreb', blank=True)),
                ('nb_sieges_moyen_orient', models.IntegerField(null=True, verbose_name='Moyen-Orient', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
