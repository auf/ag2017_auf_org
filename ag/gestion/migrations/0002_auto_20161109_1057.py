# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reference', '0001_initial'),
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionWeb',
            fields=[
            ],
            options={
                'ordering': ['date_fermeture'],
                'verbose_name': 'Inscription',
                'proxy': True,
            },
            bases=('inscription.inscription',),
        ),
        migrations.AddField(
            model_name='reservationchambre',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='participationactivite',
            name='activite',
            field=models.ForeignKey(to='gestion.Activite'),
        ),
        migrations.AddField(
            model_name='participationactivite',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='participant',
            name='activite_scientifique',
            field=models.ForeignKey(blank=True, to='gestion.ActiviteScientifique', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='activites',
            field=models.ManyToManyField(to='gestion.Activite', through='gestion.ParticipationActivite'),
        ),
        migrations.AddField(
            model_name='participant',
            name='etablissement',
            field=models.ForeignKey(db_constraint=False, verbose_name='\xc9tablissement', to='reference.Etablissement', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='forfaits',
            field=models.ManyToManyField(to='inscription.Forfait'),
        ),
        migrations.AddField(
            model_name='participant',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.Hotel', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='inscription',
            field=models.OneToOneField(null=True, to='inscription.Inscription'),
        ),
        migrations.AddField(
            model_name='participant',
            name='pays_autre_institution',
            field=models.ForeignKey(db_constraint=False, verbose_name='Pays', blank=True, to='reference.Pays', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='region',
            field=models.ForeignKey(db_constraint=False, verbose_name='R\xe9gion', to='reference.Region', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='statut',
            field=models.ForeignKey(to='gestion.StatutParticipant', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='participant',
            name='suivi',
            field=models.ManyToManyField(to='gestion.PointDeSuivi'),
        ),
        migrations.AddField(
            model_name='participant',
            name='type_autre_institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.TypeInstitutionSupplementaire', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='vol_groupe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gestion.VolGroupe', null=True),
        ),
        migrations.AddField(
            model_name='paiement',
            name='implantation',
            field=models.ForeignKey(to='reference.Implantation'),
        ),
        migrations.AddField(
            model_name='paiement',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='invite',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='infosvol',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant', null=True),
        ),
        migrations.AddField(
            model_name='infosvol',
            name='vol_groupe',
            field=models.ForeignKey(to='gestion.VolGroupe', null=True),
        ),
        migrations.AddField(
            model_name='frais',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='frais',
            name='type_frais',
            field=models.ForeignKey(to='gestion.TypeFrais'),
        ),
        migrations.AddField(
            model_name='fichier',
            name='cree_par',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='efface_par',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fichier',
            name='participant',
            field=models.ForeignKey(to='gestion.Participant'),
        ),
        migrations.AddField(
            model_name='chambre',
            name='hotel',
            field=models.ForeignKey(to='gestion.Hotel'),
        ),
        migrations.AddField(
            model_name='agrole',
            name='region',
            field=models.ForeignKey(db_constraint=False, verbose_name='R\xe9gion', blank=True, to='reference.Region', null=True),
        ),
        migrations.AddField(
            model_name='agrole',
            name='user',
            field=models.ForeignKey(related_name='roles', verbose_name='utilisateur', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activite',
            name='forfait_invite',
            field=models.ForeignKey(verbose_name='Forfait invit\xe9 correspondant', blank=True, to='inscription.Forfait', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='reservationchambre',
            unique_together=set([('participant', 'type_chambre')]),
        ),
        migrations.AlterUniqueTogether(
            name='participationactivite',
            unique_together=set([('activite', 'participant')]),
        ),
        migrations.AlterUniqueTogether(
            name='chambre',
            unique_together=set([('hotel', 'type_chambre')]),
        ),
    ]
