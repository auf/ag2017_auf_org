# encoding: utf-8
import collections
import datetime
import random
import string
import urllib2
from urllib import unquote_plus
import uuid

from auf.django.mailing.models import Enveloppe, TAILLE_JETON, generer_jeton
from django.db.models import Sum
import requests
from ag.reference.models import Etablissement
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.dispatch.dispatcher import Signal
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from ag.core import models as core
from ag.gestion.montants import get_infos_montants, infos_montant_par_code


class LigneFacture(object):
    def __init__(self, infos_montant, quantite=1, montant=None):
        self.infos_montant = infos_montant
        self.quantite = quantite
        self.montant = montant or infos_montant.montant

    def total(self):
        return self.montant * self.quantite


class RenseignementsPersonnels(models.Model):

    class Meta:
        abstract = True

    GENRE_CHOICES = (
        ('M', 'M.'),
        ('F', 'Mme'),
        )

    PAIEMENT_CHOICES = (
        ('CB', 'Carte bancaire'),
        ('VB', 'Virement bancaire'),
        ('CE', 'Chèque en euros'),
        ('DL', 'Devises locales'),
        )

    genre = models.CharField(
        'civilité', max_length=1, choices=GENRE_CHOICES, blank=True
    )
    nom = models.CharField(
        'nom', max_length=100, help_text=u'tel que sur le passeport'
    )
    prenom = models.CharField(
        'prénom(s)', max_length=100, help_text=u'tel que sur le passeport'
    )
    nationalite = models.CharField('nationalité', max_length=100, blank=True)
    date_naissance = models.DateField(
        '   Date de naissance', blank=True, null=True,
        help_text=u'format: jj/mm/aaaa'
    )
    poste = models.CharField('poste occupé', max_length=100, blank=True)
    courriel = models.EmailField(blank=True)
    adresse = models.TextField(
        'Adresse de facturation', blank=True,
        help_text=(
            u"Ceci est l'adresse de votre établissement. "
            u"Modifiez ces données pour changer l'adresse de facturation."
        )
    )
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)
    code_postal = models.CharField(max_length=20, blank=True)
    telephone = models.CharField('téléphone', max_length=50, blank=True)
    telecopieur = models.CharField('télécopieur', max_length=50, blank=True)

    DATE_HOTEL_MIN = datetime.date(2013, 5, 6)
    DATE_HOTEL_MAX = datetime.date(2013, 5, 8)

    date_arrivee_hotel = models.DateField(
        u"Date d'arrivée", null=True, blank=True
    )
    date_depart_hotel = models.DateField(
        u"Date de départ", null=True, blank=True
    )

    # Options de paiement
    paiement = models.CharField(
        'modalités de paiement', max_length=2, choices=PAIEMENT_CHOICES,
        blank=True
    )

    def save(self, **kwargs):
        self.nom = self.nom.upper()
        return super(RenseignementsPersonnels, self).save(**kwargs)


class Invitation(models.Model):
    etablissement = models.ForeignKey(Etablissement)
    pour_mandate = models.BooleanField(default=False)
    courriel = models.EmailField(null=True)  # si non spécifié par établissement
    jeton = models.CharField(max_length=TAILLE_JETON, default=generer_jeton)

    def get_region(self):
        return self.etablissement.region

    def get_adresse(self):
        if hasattr(settings, 'MAILING_TEST_ADDRESS'):
            return settings.MAILING_TEST_ADDRESS
        else:
            return self.courriel or self.etablissement.responsable_courriel

    def get_nom_destinataire(self):
        return self.etablissement.nom


class InvitationEnveloppe(models.Model):
    enveloppe = models.OneToOneField(Enveloppe)
    invitation = models.ForeignKey(Invitation)

    def get_adresse(self):
        return self.invitation.get_adresse()

    def get_corps_context(self):
        context = {
            'nom_destinataire': self.invitation.get_nom_destinataire(),
            'nom_etablissement': self.invitation.etablissement.nom,
            'jeton': self.invitation.jeton,
            'url': 'https://%s%s' % (
                Site.objects.get(id=1).domain,
                reverse('connexion_inscription', args=(self.invitation.jeton,))
            )
        }
        return context

# À certains champs correspondent des montants (ex:
CODES_CHAMPS_MONTANTS = {
    'programmation_soiree_9_mai': 'soiree_9_mai_membre',
    'programmation_soiree_9_mai_invite': 'soiree_9_mai_invite',
    'programmation_soiree_10_mai': 'soiree_10_mai_membre',
    'programmation_soiree_10_mai_invite': 'soiree_10_mai_invite',
    'programmation_gala': 'gala_membre',
    'programmation_gala_invite': 'gala_invite',
    'forfait_invite_dejeuners': 'forfait_invite_dejeuners',
    'forfait_invite_transfert': 'forfait_invite_transfert',
}


paypal_signal = Signal()


class Inscription(RenseignementsPersonnels):

    DEPART_DE_CHOICES = (
        ('sao-paulo', u'São Paulo'),
        ('rio', u'Rio de Janeiro'),
    )

    invitation = models.OneToOneField(Invitation)

    # Accueil
    identite_confirmee = models.BooleanField('identité confirmée',
                                             default=False)
    conditions_acceptees = models.BooleanField(
        mark_safe(
            u'J\'ai lu et j\'accepte les '
            u'<a href="/inscription/conditions-generales/" '
            u'onclick="javascript:window.open'
            u'(\'/inscription/conditions-generales/\');return false;" '
            u'target="_blank">conditions générales d\'inscription</a>'
        ),
        default=False
    )

    # Renseignements personnels

    # Accompagnateur
    accompagnateur = models.BooleanField(
        u"Je serai accompagné(e) par une autre personne qui ne participera "
        u"pas à l'assemblée générale",
        default=False
    )
    accompagnateur_genre = models.CharField(
        u'genre', max_length=1,
        choices=RenseignementsPersonnels.GENRE_CHOICES, blank=True
    )
    accompagnateur_nom = models.CharField('nom', max_length=100, blank=True)
    accompagnateur_prenom = models.CharField(
        u'prénom(s)', max_length=100, blank=True
    )

    # Programmation
    programmation_soiree_9_mai = models.BooleanField(
        u"Je participerai à la soirée du 9 mai.", default=False)
    programmation_soiree_9_mai_invite = models.BooleanField(
        u"Dîner du 9 mai", default=False)
    programmation_soiree_10_mai = models.BooleanField(
        u"Je participerai à la soirée du 10 mai.", default=False)
    programmation_soiree_10_mai_invite = models.BooleanField(
        u"Dîner du 10 mai", default=False)
    programmation_gala = models.BooleanField(
        u"Je participerai à la soirée de gala de clôture de l'assemblée "
        u"générale le 11 mai", default=False)
    programmation_gala_invite = models.BooleanField(
        u"Dîner de gala du 11 mai", default=False)
    forfait_invite_dejeuners = models.BooleanField(
        u"Forfait 3 Déjeuners (9,10 et 11)", default=False)
    forfait_invite_transfert = models.BooleanField(
        u"2 transferts aéroport et hôtel (seulement si votre accompagnateur "
        u"voyage avec vous)", default=False)

    # Transport et hébergement
    prise_en_charge_hebergement = models.NullBooleanField(
        "Je demande la prise en charge de mon hébergement."
    )
    prise_en_charge_transport = models.NullBooleanField(
        "Je demande la prise en charge de mon transport."
    )

    type_chambre_hotel = models.CharField(
        max_length=1, null=True, blank=True,
        choices=(('1', "chambre avec 1 lit simple"),
                 ('2', "chambre double (supplément de 100€)"),))

    arrivee_date = models.DateField(
        "date d'arrivée à São Paulo", blank=True, null=True,
        help_text='format: jj/mm/aaaa'
    )
    arrivee_heure = models.TimeField(
        'heure', blank=True, null=True, help_text='format: hh:mm'
    )
    arrivee_compagnie = models.CharField(
        'compagnie', max_length=100, blank=True
    )
    arrivee_vol = models.CharField('vol', max_length=100, blank=True)
    depart_de = models.CharField(
        'départ de', max_length=10, choices=DEPART_DE_CHOICES, blank=True
    )
    depart_date = models.DateField(
        "date de départ de São Paulo", blank=True, null=True,
        help_text='format: jj/mm/aaaa'
    )
    depart_heure = models.TimeField(
        'heure', blank=True, null=True, help_text='format: hh:mm'
    )
    depart_compagnie = models.CharField(
        'compagnie', max_length=100, blank=True
    )
    depart_vol = models.CharField('vol', max_length=100, blank=True)

    fermee = models.BooleanField(
        u"Confirmée par le participant", default=False
    )
    date_fermeture = models.DateField(u"Confirmée le", null=True)
#     paypal_cancel = models.NullBooleanField()

    numero_dossier = models.CharField(max_length=8, unique=True, null=True)

    @property
    def numero(self):
        return 'A%04d' % self.id

    def get_region(self):
        return self.invitation.get_region()

    def make_numero_dossier(self):
        retry = True
        while retry:
            num_dossier = ''.join(random.choice(string.ascii_uppercase +
                                                string.digits)
                                  for _ in range(8))
            retry = False
            try:
                self.numero_dossier = num_dossier
                self.save()
            except IntegrityError:
                retry = True

    CHAMPS_PROGRAMMATION = (
        (programmation_soiree_9_mai, programmation_soiree_9_mai_invite),
        (programmation_soiree_10_mai, programmation_soiree_10_mai_invite),
        (programmation_gala, programmation_gala_invite),
    )

    def append_code_montant(self, liste, champ):
        if getattr(self, champ.name):
            liste.append(CODES_CHAMPS_MONTANTS[champ.name])

    # noinspection PyTypeChecker
    def get_liste_codes_frais(self):
        liste = ['frais_inscription']
        if self.accompagnateur:
            if self.prise_en_charge_hebergement:
                liste.append('supplement_chambre_double')
        for champ_membre, champ_invite in self.CHAMPS_PROGRAMMATION:
            self.append_code_montant(liste, champ_membre)
            if self.accompagnateur:
                self.append_code_montant(liste, champ_invite)
        if self.forfait_invite_transfert:
            liste.append(CODES_CHAMPS_MONTANTS['forfait_invite_transfert'])
        if self.forfait_invite_dejeuners:
            liste.append(CODES_CHAMPS_MONTANTS['forfait_invite_dejeuners'])
        return liste

    def get_facture(self):
        lignes = []
        for code_montant in self.get_liste_codes_frais():
            infos_montant = infos_montant_par_code(code_montant)
            ligne = LigneFacture(infos_montant)
            lignes.append(ligne)
        return lignes

    def get_montant_total(self):
        total = 0
        for ligne in self.get_facture():
            total += ligne.total()
        return int(total)

    def get_montant_a_payer(self):
        return self.get_montant_total() - self.paiement_paypal_total()

    def get_total_programmation(self):
        return self.get_total_categorie('insc') + \
               self.get_total_categorie('acti') + \
               self.get_total_categorie('invite')

    def get_total_activites(self):
        return self.get_total_categorie('acti') + \
               self.get_total_categorie('invite')

    def get_total_categorie(self, cat):
        total = 0
        for ligne in self.get_facture():
            if ligne.infos_montant.categorie == cat:
                total += ligne.total()
        return total

    def get_total_du(self):
        return self.get_montant_total() - self.paiement_paypal_total()

    def get_frais_inscription(self):
        return self.get_total_categorie('insc')

    def get_liste_activites(self):
        liste = []
        liste_codes = frozenset(self.get_liste_codes_frais())
        for code, infos_montant in get_infos_montants().iteritems():
            if code in liste_codes and infos_montant.categorie == 'acti':
                liste.append(infos_montant)
        return liste

    def get_etablissement(self):
        return self.invitation.etablissement

    def etablissement_delinquant(self):
        return core.EtablissementDelinquant.objects.filter(
            id=self.invitation.etablissement.id
        ).exists()

    def est_pour_mandate(self):
        return self.invitation.pour_mandate

    def est_pour_sud(self):
        return self.invitation.etablissement.pays.sud

    def get_est_pour_sud_display(self):
        return "sud" if self.est_pour_sud() else "nord"

    def get_jeton(self):
        return self.invitation.enveloppe.jeton

    def preremplir(self):
        etablissement = self.get_etablissement()
        self.adresse = etablissement.nom + "\n" + etablissement.adresse
        self.ville = etablissement.ville
        self.code_postal = etablissement.code_postal
        self.pays = etablissement.pays.nom
        self.telephone = etablissement.telephone
        self.courriel = self.invitation.get_adresse()
        if self.est_pour_mandate():
            self.nom = etablissement.responsable_nom
            self.prenom = etablissement.responsable_prenom
            self.genre = etablissement.responsable_genre
            self.poste = etablissement.responsable_fonction

    def get_invitations_accompagnateurs(self):
        if self.est_pour_mandate():
            invitations = Invitation.objects.filter(
                etablissement=self.get_etablissement(),
                pour_mandate=False)
            return invitations

    def prise_en_charge_possible(self):
        return self.prise_en_charge_hebergement_possible() or \
            self.prise_en_charge_transport_possible()

    def prise_en_charge_hebergement_possible(self):
        return (self.est_pour_mandate() and self.est_pour_sud() and
                self.get_etablissement().statut in ("T", "A"))

    def prise_en_charge_transport_possible(self):
        return (
            self.est_pour_mandate() and self.est_pour_sud() and
            self.get_etablissement().statut == "T"
        )

    def paiement_paypal_ok(self):
        return PaypalResponse.objects.accepted(self).exists()

    def paiement_paypal_total(self):
        return PaypalResponse.objects.accepted(self).aggregate(
            total=Sum('montant'))['total'] or 0

    def numeros_confirmation_paypal(self):
        return u', '.join([
            paiement.numero_transaction
            for paiement in PaypalResponse.objects.accepted(self)])

    def statut_paypal_text(self):
        if self.paiement_paypal_ok():
            return u' (PAYPAL OK, ' + str(self.paiement_paypal_total()) + u'€)'
        else:
            return u' (PAYPAL NON REÇU)'

    def fermer(self):
        if not self.prise_en_charge_hebergement_possible():
            self.prise_en_charge_hebergement = False
        if not self.prise_en_charge_transport_possible():
            self.prise_en_charge_transport = False
        self.fermee = True
        self.date_fermeture = datetime.datetime.now().date()
        self.save()

    def __unicode__(self):
        return self.nom.upper() + u', ' + self.prenom + u' (' \
            + self.get_etablissement().nom + u')'


class PaypalInvoice(models.Model):
    inscription = models.ForeignKey(Inscription)
    invoice_uid = models.UUIDField(default=uuid.uuid4, db_index=True)
    montant = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


class PaypalResponseManager(models.Manager):
    def accepted(self, inscription):
        return self.filter(inscription=inscription,
                           statut__in=PaypalResponse.STATUS_ACCEPTED,
                           montant__isnull=False)


class PaypalResponse(models.Model):
    STATUS_ACCEPTED = ['Processed', 'Completed']

    type_reponse = models.CharField(max_length=3, choices=(
        ('IPN', u"Instant Payment Notification"),
        ('PDT', u"Payment Data Transfer"),
        ('CAN', u"Cancelled"),
    ))
    inscription = models.ForeignKey(Inscription, null=True)

    date_heure = models.DateTimeField(
        verbose_name=u'Date et heure du paiement', null=True
    )
    montant = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    devise = models.CharField(max_length=32, null=True)
    invoice_uid = models.UUIDField(db_index=True, null=True)
    txn_id = models.CharField(max_length=250, db_index=True, null=True)
    statut = models.CharField(max_length=64, null=True)
    raison_attente = models.CharField(max_length=128, null=True)
    request_data = models.TextField(null=True)
    validation_response_data = models.TextField(null=True)
    validated = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    objects = PaypalResponseManager()

PDTResponse = collections.namedtuple('PDTResponse', ('valid', 'raw_response',
                                                     'response_dict'))


def validate_pdt(tx_id):
    postback_dict = {
        'cmd': "_notify-synch",
        'at': settings.PAYPAL_PDT_TOKEN,
        'tx': tx_id,
    }
    postback_params = urlencode(postback_dict)
    response = urllib2.urlopen(settings.PAYPAL_URL, postback_params).read()
    lignes = response.split('\n')
    valid = unquote_plus(lignes[0]) == 'SUCCESS'
    d = {}
    for ligne in lignes[1:]:
        ligne = unquote_plus(ligne)
        if "=" in ligne:
            key, value = ligne.split("=")
            d[key] = value
    return PDTResponse(valid=valid, raw_response=response, response_dict=d)


def is_ipn_valid(request):
    print("cmd=_notify-validate&" + request.body)
    response = requests.post(
        settings.PAYPAL_URL,
        data="cmd=_notify-validate&" + request.body)
    return response.text == 'VERIFIED', response.text
