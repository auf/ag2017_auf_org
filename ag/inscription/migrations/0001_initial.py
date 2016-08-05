# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import auf.django.mailing.models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '__first__'),
        ('reference', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('genre', models.CharField(blank=True, max_length=1, verbose_name=b'civilit\xc3\xa9', choices=[(b'M', b'M.'), (b'F', b'Mme')])),
                ('nom', models.CharField(help_text='tel que sur le passeport', max_length=100, verbose_name=b'nom')),
                ('prenom', models.CharField(help_text='tel que sur le passeport', max_length=100, verbose_name=b'pr\xc3\xa9nom(s)')),
                ('nationalite', models.CharField(max_length=100, verbose_name=b'nationalit\xc3\xa9', blank=True)),
                ('date_naissance', models.DateField(help_text='format: jj/mm/aaaa', null=True, verbose_name=b'   Date de naissance', blank=True)),
                ('poste', models.CharField(max_length=100, verbose_name=b'poste occup\xc3\xa9', blank=True)),
                ('courriel', models.EmailField(max_length=254, blank=True)),
                ('adresse', models.TextField(help_text="Ceci est l'adresse de votre \xe9tablissement. Modifiez ces donn\xe9es pour changer l'adresse de facturation.", verbose_name=b'Adresse de facturation', blank=True)),
                ('ville', models.CharField(max_length=100, blank=True)),
                ('pays', models.CharField(max_length=100, blank=True)),
                ('code_postal', models.CharField(max_length=20, blank=True)),
                ('telephone', models.CharField(max_length=50, verbose_name=b't\xc3\xa9l\xc3\xa9phone', blank=True)),
                ('telecopieur', models.CharField(max_length=50, verbose_name=b't\xc3\xa9l\xc3\xa9copieur', blank=True)),
                ('date_arrivee_hotel', models.DateField(null=True, verbose_name="Date d'arriv\xe9e", blank=True)),
                ('date_depart_hotel', models.DateField(null=True, verbose_name='Date de d\xe9part', blank=True)),
                ('paiement', models.CharField(blank=True, max_length=2, verbose_name=b'modalit\xc3\xa9s de paiement', choices=[(b'CB', b'Carte bancaire'), (b'VB', b'Virement bancaire'), (b'CE', b'Ch\xc3\xa8que en euros'), (b'DL', b'Devises locales')])),
                ('identite_confirmee', models.BooleanField(default=False, verbose_name=b'identit\xc3\xa9 confirm\xc3\xa9e')),
                ('conditions_acceptees', models.BooleanField(default=False, verbose_name='J\'ai lu et j\'accepte les <a href="/inscription/conditions-generales/" onclick="javascript:window.open(\'/inscription/conditions-generales/\');return false;" target="_blank">conditions g\xe9n\xe9rales d\'inscription</a>')),
                ('accompagnateur', models.BooleanField(default=False, verbose_name="Je serai accompagn\xe9(e) par une autre personne qui ne participera pas \xe0 l'assembl\xe9e g\xe9n\xe9rale")),
                ('accompagnateur_genre', models.CharField(blank=True, max_length=1, verbose_name='genre', choices=[(b'M', b'M.'), (b'F', b'Mme')])),
                ('accompagnateur_nom', models.CharField(max_length=100, verbose_name=b'nom', blank=True)),
                ('accompagnateur_prenom', models.CharField(max_length=100, verbose_name='pr\xe9nom(s)', blank=True)),
                ('programmation_soiree_unesp', models.BooleanField(default=False, verbose_name="Je participerai \xe0 la soir\xe9e organis\xe9e par l'UNESP le 7 mai 2013.")),
                ('programmation_soiree_unesp_invite', models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.')),
                ('programmation_soiree_interconsulaire', models.BooleanField(default=False, verbose_name='Je participerai \xe0 la soir\xe9e interconsulaire le 8 mai 2013.')),
                ('programmation_soiree_interconsulaire_invite', models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.')),
                ('programmation_gala', models.BooleanField(default=False, verbose_name="Je participerai \xe0 la soir\xe9e de gala de cl\xf4ture de l'assembl\xe9e g\xe9n\xe9rale le 9 mai 2013.")),
                ('programmation_gala_invite', models.BooleanField(default=False, verbose_name='Mon invit\xe9 \xe9galement.')),
                ('prise_en_charge_hebergement', models.NullBooleanField(verbose_name=b'Je demande la prise en charge de mon h\xc3\xa9bergement.')),
                ('prise_en_charge_transport', models.NullBooleanField(verbose_name=b'Je demande la prise en charge de mon transport.')),
                ('arrivee_date', models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b"date d'arriv\xc3\xa9e \xc3\xa0 S\xc3\xa3o Paulo", blank=True)),
                ('arrivee_heure', models.TimeField(help_text=b'format: hh:mm', null=True, verbose_name=b'heure', blank=True)),
                ('arrivee_compagnie', models.CharField(max_length=100, verbose_name=b'compagnie', blank=True)),
                ('arrivee_vol', models.CharField(max_length=100, verbose_name=b'vol', blank=True)),
                ('depart_de', models.CharField(blank=True, max_length=10, verbose_name=b'd\xc3\xa9part de', choices=[(b'sao-paulo', 'S\xe3o Paulo'), (b'rio', 'Rio de Janeiro')])),
                ('depart_date', models.DateField(help_text=b'format: jj/mm/aaaa', null=True, verbose_name=b'date de d\xc3\xa9part de S\xc3\xa3o Paulo', blank=True)),
                ('depart_heure', models.TimeField(help_text=b'format: hh:mm', null=True, verbose_name=b'heure', blank=True)),
                ('depart_compagnie', models.CharField(max_length=100, verbose_name=b'compagnie', blank=True)),
                ('depart_vol', models.CharField(max_length=100, verbose_name=b'vol', blank=True)),
                ('fermee', models.BooleanField(default=False, verbose_name='Confirm\xe9e par le participant')),
                ('date_fermeture', models.DateField(null=True, verbose_name='Confirm\xe9e le')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pour_mandate', models.BooleanField(default=False)),
                ('courriel', models.EmailField(max_length=254, null=True)),
                ('jeton', models.CharField(default=auf.django.mailing.models.generer_jeton, max_length=32)),
                ('etablissement', models.ForeignKey(to='reference.Etablissement')),
            ],
        ),
        migrations.CreateModel(
            name='InvitationEnveloppe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enveloppe', models.OneToOneField(to='mailing.Enveloppe')),
                ('invitation', models.ForeignKey(to='inscription.Invitation')),
            ],
        ),
        migrations.CreateModel(
            name='PaiementPaypal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_heure', models.DateTimeField(null=True, verbose_name='Date et heure du paiement')),
                ('montant', models.FloatField(null=True)),
                ('devise', models.CharField(max_length=32, null=True)),
                ('numero_transaction', models.CharField(unique=True, max_length=250, db_index=True)),
                ('statut', models.CharField(max_length=64, null=True)),
                ('raison_attente', models.CharField(max_length=128, null=True)),
                ('ipn_post_data', models.TextField(null=True)),
                ('pdt_reponse', models.TextField(null=True)),
                ('ipn_valide', models.BooleanField(default=False)),
                ('pdt_valide', models.BooleanField(default=False)),
                ('inscription', models.ForeignKey(to='inscription.Inscription', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='inscription',
            name='invitation',
            field=models.OneToOneField(to='inscription.Invitation'),
        ),
    ]
