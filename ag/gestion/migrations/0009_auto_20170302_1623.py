# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
        ('gestion', '0008_auto_20170221_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='candidat_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='elections.Election', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='candidat_elimine',
            field=models.BooleanField(default=False, verbose_name='\xe9limin\xe9'),
        ),
        migrations.AddField(
            model_name='participant',
            name='candidat_libre',
            field=models.BooleanField(default=False, verbose_name='libre'),
        ),
        migrations.AddField(
            model_name='participant',
            name='suppleant_de',
            field=models.ForeignKey(blank=True, to='gestion.Participant', null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='imputation',
            field=models.CharField(blank=True, max_length=32, choices=[(b'A0394DRI017B3', b'A0394DRI017B3'), (b'A0394DRI016A3', b'A0394DRI016A3'), (b'S0255DRI017E1', b'S0255DRI017E1'), (b'S0256DRI017E1', b'S0256DRI017E1'), (b'A0394MGP017B1', b'A0394MGP017B1')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='modalite_retrait_billet',
            field=models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de retrait du billet', choices=[('0', "Vos billets vous seront transmis par l'AUF"), ('1', 'Vos billets seront disponibles au comptoir de la compagnie a\xe9rienne')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='modalite_versement_frais_sejour',
            field=models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de versement', choices=[(b'A', "Lors de votre enregistrement \xe0 l'assembl\xe9e \xe0 Marrakech"), (b'I', 'Au bureau AUF le plus proche'), (b'V', 'Par virement bancaire')]),
        ),
    ]
