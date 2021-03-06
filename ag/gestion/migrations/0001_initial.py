# -*- coding: utf-8 -*-


from django.db import migrations, models
import auf.django.permissions
import ag.gestion.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('etablissement_nom', models.CharField(max_length=765)),
                ('etablissement_id', models.IntegerField(serialize=False, primary_key=True)),
                ('etablissement_region_id', models.IntegerField(null=True, blank=True)),
                ('jeton', models.CharField(max_length=96)),
                ('enveloppe_id', models.IntegerField()),
                ('modele_id', models.IntegerField()),
                ('sud', models.BooleanField()),
                ('statut', models.CharField(max_length=3, blank=True)),
            ],
            options={
                'verbose_name': 'Invitation',
                'db_table': 'invitations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Activite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
            ],
            options={
                'verbose_name': 'Activit\xe9',
            },
        ),
        migrations.CreateModel(
            name='ActiviteScientifique',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('max_participants', models.IntegerField(default=999, verbose_name='Nb de places')),
            ],
            options={
                'ordering': ['libelle'],
                'verbose_name': 'activit\xe9 scientifique',
                'verbose_name_plural': 'activit\xe9s scientifiques',
            },
        ),
        migrations.CreateModel(
            name='AGRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_role', models.CharField(max_length=1, verbose_name='Type', choices=[(b'C', 'Comptable'), (b'I', 'SAI'), (b'L', 'Lecteur'), (b'A', 'Admin'), (b'S', 'S\xe9jour')])),
            ],
            options={
                'verbose_name': 'R\xf4le utilisateur',
                'verbose_name_plural': 'R\xf4les des utilisateurs',
            },
            bases=(models.Model, auf.django.permissions.Role),
        ),
        migrations.CreateModel(
            name='Chambre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_chambre', models.CharField(max_length=1, verbose_name='Type de chambre', choices=[(b'S', 'Chambre simple'), (b'D', 'Chambre double'), (b'1', 'Chambre simple sup\xe9rieure'), (b'2', 'Chambre double sup\xe9rieure'), (b'L', 'Chambre Luxo (simple)'), (b'A', 'Chambre anti-allerg\xe9nique')])),
                ('places', models.IntegerField()),
                ('nb_total', models.IntegerField(null=True)),
                ('prix', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Fichier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fichier', models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'/media/benselme/data/dev/projects/auf/ag2017_auf_org/medias_participants'), upload_to=ag.gestion.models.get_participant_file_path)),
                ('type_fichier', models.IntegerField(default=0, choices=[(0, 'Autres'), (1, 'Passeport')])),
                ('cree_le', models.DateTimeField(auto_now_add=True, verbose_name='cr\xe9\xe9 le ')),
                ('efface_le', models.DateTimeField(null=True, verbose_name='effac\xe9 le ')),
            ],
        ),
        migrations.CreateModel(
            name='Frais',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantite', models.IntegerField(default=1, verbose_name='quantit\xe9')),
                ('montant', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('adresse', models.TextField()),
                ('telephone', models.CharField(max_length=32, blank=True)),
                ('courriel', models.EmailField(max_length=254, blank=True)),
                ('cacher_dans_tableau_de_bord', models.BooleanField(default=False, verbose_name='Ne pas montrer dans le tableau de bord')),
            ],
            options={
                'verbose_name': 'H\xf4tel',
                'verbose_name_plural': 'H\xf4tels',
            },
        ),
        migrations.CreateModel(
            name='InfosVol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ville_depart', models.CharField(max_length=128, verbose_name='Ville de d\xe9part', blank=True)),
                ('date_depart', models.DateField(null=True, verbose_name='Date de d\xe9part', blank=True)),
                ('heure_depart', models.TimeField(null=True, verbose_name='Heure de d\xe9part', blank=True)),
                ('ville_arrivee', models.CharField(max_length=128, verbose_name="Ville d'arriv\xe9e", blank=True)),
                ('date_arrivee', models.DateField(null=True, verbose_name="Date d'arriv\xe9e", blank=True)),
                ('heure_arrivee', models.TimeField(null=True, verbose_name="Heure d'arriv\xe9e", blank=True)),
                ('numero_vol', models.CharField(max_length=16, verbose_name='N\xb0 vol', blank=True)),
                ('compagnie', models.CharField(max_length=64, blank=True)),
                ('prix', models.FloatField(null=True, blank=True)),
                ('type_infos', models.IntegerField(default=2, choices=[(0, 'Arriv\xe9e seulement'), (1, 'D\xe9part seulement'), (2, "Vol organis\xe9 par l'AUF"), (3, 'Vol group\xe9')])),
            ],
            options={
                'ordering': ['date_depart', 'heure_depart'],
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('genre', models.CharField(max_length=1, choices=[(b'M', 'M.'), (b'F', 'Mme')])),
                ('nom', models.CharField(max_length=100, verbose_name=b'nom')),
                ('prenom', models.CharField(max_length=100, verbose_name=b'pr\xc3\xa9nom(s)')),
            ],
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('montant_euros', models.DecimalField(verbose_name='Montant (\u20ac)', max_digits=10, decimal_places=2)),
                ('moyen', models.CharField(max_length=2, verbose_name='modalit\xe9', choices=[(b'CB', 'Carte bancaire'), (b'VB', 'Virement bancaire'), (b'CE', 'Ch\xe8que en euros'), (b'DL', 'Devises locales')])),
                ('ref', models.CharField(max_length=255, verbose_name='r\xe9f\xe9rence')),
                ('montant_devise_locale', models.DecimalField(null=True, verbose_name='paiement en devises locales', max_digits=16, decimal_places=2, blank=True)),
                ('devise_locale', models.CharField(max_length=3, null=True, verbose_name='devise paiement', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('genre', models.CharField(blank=True, max_length=1, verbose_name=b'civilit\xc3\xa9', choices=[(b'M', 'M.'), (b'F', 'Mme')])),
                ('nom', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nom')),
                ('prenom', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'pr\xc3\xa9nom(s)')),
                ('nationalite', models.CharField(help_text='identique au passeport', max_length=100, verbose_name=b'nationalit\xc3\xa9', blank=True)),
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
                ('utiliser_adresse_gde', models.BooleanField(default=False, verbose_name='Utiliser adresse GDE pour la facturation')),
                ('notes', models.TextField(blank=True)),
                ('notes_statut', models.TextField(blank=True)),
                ('desactive', models.BooleanField(default=False, verbose_name='D\xe9sactiv\xe9')),
                ('type_institution', models.CharField(max_length=1, verbose_name="Type de l'institution repr\xe9sent\xe9e", choices=[(b'E', '\xc9tablissement'), (b'I', "Instance de l'AUF"), (b'A', 'Autre')])),
                ('instance_auf', models.CharField(max_length=1, verbose_name="Instance de l'AUF", choices=[(b'A', "Conseil d'administration"), (b'S', 'Conseil scientifique'), (b'C', 'Conseil associatif')])),
                ('nom_autre_institution', models.CharField(max_length=64, null=True, verbose_name="Nom de l'institution")),
                ('numero_facture', models.IntegerField(null=True, verbose_name='Num\xe9ro de facture')),
                ('date_facturation', models.DateField(null=True, verbose_name='Date de facturation', blank=True)),
                ('facturation_validee', models.BooleanField(default=False, verbose_name='Facturation valid\xe9e')),
                ('notes_facturation', models.TextField(blank=True)),
                ('prise_en_charge_inscription', models.BooleanField(default=False, verbose_name="Prise en charge frais d'inscription")),
                ('prise_en_charge_transport', models.NullBooleanField(verbose_name='Prise en charge transport')),
                ('prise_en_charge_sejour', models.NullBooleanField(verbose_name='Prise en charge s\xe9jour')),
                ('prise_en_charge_activites', models.BooleanField(default=False, verbose_name='Prise en charge activit\xe9s')),
                ('imputation', models.CharField(blank=True, max_length=32, choices=[(b'90002AG201', b'90002AG201'), (b'90002AG202', b'90002AG202'), (b'90002AG203', b'90002AG203')])),
                ('modalite_versement_frais_sejour', models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de versement', choices=[(b'A', '\xc0 votre arriv\xe9e \xe0 Sao paulo'), (b'I', 'Par le bureau r\xe9gional')])),
                ('transport_organise_par_auf', models.BooleanField(default=False, verbose_name="Transport organis\xe9 par l'AUF")),
                ('statut_dossier_transport', models.CharField(blank=True, max_length=1, verbose_name='Statut dossier', choices=[(b'E', 'En cours'), (b'C', 'Compl\xe9t\xe9')])),
                ('modalite_retrait_billet', models.CharField(blank=True, max_length=1, verbose_name='Modalit\xe9 de retrait du billet', choices=[('0', 'Vos billets vous seront transmis par votre bureau r\xe9gional'), ('1', 'Vos billets seront disponibles au comptoir de la compagnie a\xe9rienne'), ('3', "Vos bilets de train et d'avion vous seront transmis par votre bureau r\xe9gional"), ('4', "Vos bilets de train et d'avion seront disponibles aux comptoirs de la compagnie a\xe9rienne et de la SNCF")])),
                ('numero_dossier_transport', models.CharField(max_length=32, verbose_name='num\xe9ro de dossier', blank=True)),
                ('notes_transport', models.TextField(verbose_name='Notes', blank=True)),
                ('remarques_transport', models.TextField(verbose_name='Remarques reprises sur itin\xe9raire', blank=True)),
                ('reservation_hotel_par_auf', models.BooleanField(default=False, verbose_name="r\xe9servation d'un h\xf4tel")),
                ('notes_hebergement', models.TextField(verbose_name='notes h\xe9bergement', blank=True)),
                ('commentaires', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParticipationActivite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('avec_invites', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PointDeSuivi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('ordre', models.IntegerField()),
            ],
            options={
                'ordering': ['ordre'],
                'verbose_name': 'Point de suivi participant',
                'verbose_name_plural': 'Points de suivi participants',
            },
        ),
        migrations.CreateModel(
            name='ReservationChambre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type_chambre', models.CharField(max_length=1, choices=[(b'S', 'Chambre simple'), (b'D', 'Chambre double'), (b'1', 'Chambre simple sup\xe9rieure'), (b'2', 'Chambre double sup\xe9rieure'), (b'L', 'Chambre Luxo (simple)'), (b'A', 'Chambre anti-allerg\xe9nique')])),
                ('nombre', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='StatutParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('ordre', models.IntegerField()),
                ('droit_de_vote', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['ordre'],
                'verbose_name': 'Statut participant',
                'verbose_name_plural': 'Statuts participants',
            },
        ),
        migrations.CreateModel(
            name='TypeFrais',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
            ],
            options={
                'ordering': ['libelle'],
                'verbose_name': 'Type de frais',
                'verbose_name_plural': 'Types de frais',
            },
        ),
        migrations.CreateModel(
            name='TypeInstitutionSupplementaire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, blank=True)),
                ('libelle', models.CharField(max_length=256, verbose_name='Libell\xe9')),
                ('ordre', models.IntegerField()),
            ],
            options={
                'ordering': ['ordre'],
                'verbose_name': "Type d'institution suppl\xe9mentaire",
                'verbose_name_plural': "Types d'institutions suppl\xe9mentaires",
            },
        ),
        migrations.CreateModel(
            name='VolGroupe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=256)),
                ('nombre_de_sieges', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['nom'],
            },
        ),
    ]
