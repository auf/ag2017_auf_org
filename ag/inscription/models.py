# encoding: utf-8
import collections
import datetime
import random
import string
import urllib2
from urllib import unquote_plus
import uuid

from auf.django.mailing.models import Enveloppe, TAILLE_JETON, generer_jeton
import requests
from django.utils.formats import date_format, number_format

from ag.gestion import consts
from ag.gestion.consts import PAIEMENT_CHOICES_DICT
from ag.inscription.templatetags.inscription import adresse_email_region
from ag.reference.models import Etablissement
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.dispatch.dispatcher import Signal
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from ag.core import models as core


class LigneFacture(object):
    def __init__(self, forfait, quantite=1, montant=None):
        self.forfait = forfait
        self.quantite = quantite
        self.montant = montant or forfait.montant

    def total(self):
        return self.montant * self.quantite


Paiement = collections.namedtuple(
    'Paiement', ('date', 'moyen', 'implantation', 'ref_paiement', 'montant'))

Adresse = collections.namedtuple(
    'Adresse', ('adresse', 'code_postal', 'ville', 'pays', 'telephone',
                'telecopieur'))


class RenseignementsPersonnels(models.Model):

    class Meta:
        abstract = True

    GENRE_CHOICES = (
        ('M', u'M.'),
        ('F', u'Mme'),
        )

    genre = models.CharField(
        'civilité', max_length=1, choices=GENRE_CHOICES, blank=True
    )
    nom = models.CharField(
        'nom', max_length=100, help_text=u'identique au passeport'
    )
    prenom = models.CharField(
        'prénom(s)', max_length=100, help_text=u'identique au passeport'
    )
    nationalite = models.CharField(
        'nationalité', max_length=100, help_text=u'identique au passeport',
        blank=True)
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

    def save(self, **kwargs):
        if self.nom:
            self.nom = self.nom.upper()
        return super(RenseignementsPersonnels, self).save(**kwargs)

    def get_paiements(self):
        """

        :return: List[Paiement]
        """
        return []

    def get_paiements_display(self):
        return [Paiement(
            date=date_format(p.date, settings.SHORT_DATE_FORMAT),
            montant=montant_str(p.montant),
            ref_paiement=p.ref_paiement,
            implantation=p.implantation,
            moyen=PAIEMENT_CHOICES_DICT[p.moyen]
        ) for p in self.get_paiements()]

    def get_adresse(self):
        return Adresse(adresse=self.adresse, ville=self.ville,
                       code_postal=self.code_postal,
                       pays=self.pays, telephone=self.telephone,
                       telecopieur=self.telecopieur)

    def get_verse_en_trop(self):
        return -min(self.total_facture - self.total_deja_paye, 0)

    def get_solde_a_payer(self):
        return max(self.total_facture - self.total_deja_paye, 0)

    def get_solde(self):
        return self.total_facture - self.total_deja_paye


class Invitation(models.Model):
    etablissement = models.ForeignKey(Etablissement)
    pour_mandate = models.BooleanField(default=False)
    courriel = models.EmailField(null=True)  # si non spécifié par établissement
    jeton = models.CharField(max_length=TAILLE_JETON, default=generer_jeton)
    # optionel, utilisé pour les invités (non mandatés)
    nom = models.CharField(max_length=100, null=True)
    prenom = models.CharField(max_length=100, null=True)

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

    def get_adresse_expediteur(self):
        return self.get_email_region()

    def get_corps_context(self):
        email_region = self.get_email_region()
        context = {
            'nom_destinataire': self.invitation.get_nom_destinataire(),
            'nom_etablissement': self.invitation.etablissement.nom,
            'jeton': self.invitation.jeton,
            'email_region': email_region,
            'url': 'https://%s%s' % (
                Site.objects.get(id=1).domain,
                reverse('connexion_inscription', args=(self.invitation.jeton,))
            )
        }
        if not self.invitation.pour_mandate:
            context['inscription_representant'] = \
                get_inscription_representant(self.invitation.etablissement)
        return context

    def get_email_region(self):
        return adresse_email_region(self.invitation.get_region().code)


# À certains champs correspondent des montants (ex:
CODES_CHAMPS_FORFAITS = {
    'programmation_soiree_9_mai_invite': consts.CODE_SOIREE_9_MAI_INVITE,
    'programmation_soiree_10_mai_invite': consts.CODE_SOIREE_10_MAI_INVITE,
    'programmation_gala_invite': consts.CODE_GALA_INVITE,
    'forfait_invite_dejeuners': consts.CODE_DEJEUNERS,
    'forfait_invite_transfert': consts.CODE_TRANSFERT_AEROPORT,
}


paypal_signal = Signal()


class Inscription(RenseignementsPersonnels):

    DEPART_DE_CHOICES = (
        ('sao-paulo', u'São Paulo'),
        ('rio', u'Rio de Janeiro'),
    )

    invitation = models.OneToOneField(Invitation)

    # Accueil
    atteste_pha = models.CharField(max_length=1, choices=(
        ('P', u"J'atteste être la plus haute autorité de mon établissement et "
              u"participerai à la 17ème Assemblée générale de l'AUF"),
        ('R', u"J'atteste être le représentant dûment mandaté par la plus "
              u"haute autorité de mon établissement pour participer à la "
              u"17ème Assemblée générale de l'AUF"),
    ), null=True)

    identite_accompagnateur_confirmee = models.BooleanField(
        'identité confirmée', default=False)
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
        u"Dîner du 9 mai à l’hôtel Mogador", default=False)
    programmation_soiree_9_mai_invite = models.BooleanField(
        u"Dîner du 9 mai à l’hôtel Mogador", default=False)
    programmation_soiree_10_mai = models.BooleanField(
        u"Soirée Fantasia \"Chez Ali\" du 10 mai.", default=False)
    programmation_soiree_10_mai_invite = models.BooleanField(
        u"Soirée Fantasia \"Chez Ali\" du 10 mai.", default=False)
    programmation_gala = models.BooleanField(
        u"Soirée de gala de clôture de l'Assemblée générale le 11 mai.",
        default=False)
    programmation_gala_invite = models.BooleanField(
        u"Soirée de gala de clôture de l'Assemblée générale le 11 mai.",
        default=False)
    programmation_soiree_12_mai = models.BooleanField(
        u"Cocktail dînatoire de clôture le 12 mai.", default=False)
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

    arrivee_date = models.DateField(
        "date d'arrivée à São Paulo", blank=True, null=True,
        help_text='format: jj/mm/aaaa'
    )
    arrivee_heure = models.TimeField(
        'heure', blank=True, null=True, help_text='format: hh:mm'
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
    depart_vol = models.CharField('vol', max_length=100, blank=True)

    fermee = models.BooleanField(
        u"Confirmée par le participant", default=False
    )
    date_fermeture = models.DateField(u"Confirmée le", null=True)
#     paypal_cancel = models.NullBooleanField()

    numero_dossier = models.CharField(max_length=8, unique=True, null=True)
    reseautage = models.BooleanField(default=False)

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
            liste.append(CODES_CHAMPS_FORFAITS[champ.name])

    def get_facturer_chambre_double(self):
        return self.accompagnateur and self.prise_en_charge_hebergement

    # noinspection PyTypeChecker
    def get_liste_codes_frais(self):
        liste = [consts.CODE_FRAIS_INSCRIPTION]
        if self.get_facturer_chambre_double():
                liste.append(consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE)
        if self.accompagnateur:
            for champ_membre, champ_invite in self.CHAMPS_PROGRAMMATION:
                self.append_code_montant(liste, champ_invite)
        if self.forfait_invite_transfert:
            liste.append(CODES_CHAMPS_FORFAITS['forfait_invite_transfert'])
        if self.forfait_invite_dejeuners:
            liste.append(CODES_CHAMPS_FORFAITS['forfait_invite_dejeuners'])
        return liste

    def get_facture(self):
        lignes = []
        forfaits = get_forfaits()
        for code_forfait in self.get_liste_codes_frais():
            ligne = LigneFacture(forfaits[code_forfait])
            lignes.append(ligne)
        return lignes

    def get_montant_total(self):
        total = 0
        for ligne in self.get_facture():
            total += ligne.total()
        return int(total)

    @property
    def total_facture(self):
        return self.get_montant_total()

    @property
    def total_deja_paye(self):
        return self.paiement_paypal_total()

    def get_montant_a_payer(self):
        return self.get_montant_total() - self.paiement_paypal_total()

    def get_total_programmation(self):
        return self.get_total_categorie(consts.CODE_CAT_INSCRIPTION) + \
               self.get_total_categorie(consts.CODE_CAT_INVITE)

    def get_total_forfaits_suppl(self):
        return self.get_total_categorie(consts.CODE_CAT_INVITE)

    def get_total_categorie(self, cat):
        total = 0
        for ligne in self.get_facture():
            if ligne.forfait.categorie == cat:
                total += ligne.total()
        return total

    def get_frais_inscription(self):
        return self.get_total_categorie(consts.CODE_CAT_INSCRIPTION)

    def get_frais_hebergement(self):
        return self.get_total_categorie(consts.CODE_CAT_HEBERGEMENT)

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

    def get_donnees_preremplir(self):
        etablissement = self.get_etablissement()
        d = {
            'adresse': etablissement.nom + '\n' + etablissement.adresse,
            'ville': etablissement.ville,
            'code_postal': etablissement.code_postal,
            'pays': etablissement.pays.nom,
            'telephone': etablissement.telephone,
        }
        if self.est_pour_mandate():
            if self.atteste_pha == 'P':
                d['nom'] = etablissement.responsable_nom
                d['prenom'] = etablissement.responsable_prenom
                d['genre'] = etablissement.responsable_genre
                d['poste'] = etablissement.responsable_fonction
                d['courriel'] = etablissement.responsable_courriel
        else:
            d['nom'] = self.invitation.nom
            d['prenom'] = self.invitation.prenom
            d['courriel'] = self.invitation.courriel
        return d

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

    def is_paiement_paypal_cancelled(self):
        return (not self.paiement_paypal_ok() and
                PaypalResponse.objects.filter(inscription=self,
                                              type_reponse='CAN').exists())

    def paiement_paypal_ok(self):
        return PaypalResponse.objects.accepted(self).exists()

    def get_unique_paypal_responses(self):
        reponses = []
        reponses_valides = PaypalResponse.objects.accepted(self)
        if reponses_valides:
            encountered_txns = set()
            for reponse in reponses_valides:
                # il peut y en avoir plusieurs (PDT/IPN)
                if reponse.txn_id not in encountered_txns:
                    reponses.append(reponse)
                    encountered_txns.add(reponse.txn_id)
        return reponses

    def paiement_paypal_total(self):
        reponses = self.get_unique_paypal_responses()
        return sum(reponse.montant for reponse in reponses)

    def numeros_confirmation_paypal(self):
        return u', '.join([
            paiement.txn_id
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

    def get_paiements(self):
        paiements = []
        for reponse in self.get_unique_paypal_responses():
            paiement = Paiement(date=reponse.received_at.date(),
                                moyen='CB',
                                montant=reponse.montant,
                                ref_paiement=reponse.txn_id,
                                implantation=u"ICA1")
            paiements.append(paiement)
        return paiements

    def get_inscription_representant_etablissement(self):
        return get_inscription_representant(self.get_etablissement())

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
                           montant__isnull=False,
                           validated=True)


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
    response = requests.post(
        settings.PAYPAL_URL,
        data="cmd=_notify-validate&" + request.body)
    return response.text == 'VERIFIED', response.text


def montant_str(montant):
    return u"{} €".format(number_format(montant, 2))


class Forfait(core.TableReference):
    montant = models.IntegerField()
    categorie = models.CharField(max_length=4,
                                 choices=consts.CATEGORIES_FORFAITS)

    def affiche(self):
        return montant_str(self.montant)


def get_forfaits():
    return {f.code: f for f in Forfait.objects.all()}


def get_inscription_representant(etablissement):
    representants = Inscription.objects.filter(
        invitation__pour_mandate=True,
        invitation__etablissement=etablissement,
    )
    if len(representants):
        return representants[0]
