# encoding: utf-8
import datetime
import urllib2
from urllib import unquote_plus

from auf.django.mailing.models import Enveloppe, TAILLE_JETON, generer_jeton
from ag.reference.models import Etablissement
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query_utils import Q
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
    courriel = models.EmailField(null=True)
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
    programmation_soiree_unesp = models.BooleanField(
        u"Je participerai à la soirée organisée par l'UNESP le 7 mai 2013.",
        default=False
    )
    programmation_soiree_unesp_invite = models.BooleanField(
        u"Mon invité également.",
        default=False
    )
    programmation_soiree_interconsulaire = models.BooleanField(
        u"Je participerai à la soirée interconsulaire le 8 mai 2013.",
        default=False
    )
    programmation_soiree_interconsulaire_invite = models.BooleanField(
        u"Mon invité également.",
        default=False
    )
    programmation_gala = models.BooleanField(
        u"Je participerai à la soirée de gala de clôture de l'assemblée "
        u"générale le 9 mai 2013.",
        default=False
    )
    programmation_gala_invite = models.BooleanField(
        u"Mon invité également.",
        default=False
    )

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

    @property
    def numero(self):
        return 'A%04d' % self.id

    def get_region(self):
        return self.invitation.get_region()

    def get_liste_codes_frais(self):
        liste = ['frais_inscription']
        if self.accompagnateur:
            liste.append('frais_inscription_invite')
            if self.prise_en_charge_hebergement:
                liste.append('supplement_chambre_double')
        if self.programmation_gala:
            liste.append('gala_membre')
            if self.accompagnateur and self.programmation_gala_invite:
                liste.append('gala_invite')
        if self.programmation_soiree_unesp:
            liste.append('sortie_unesp_membre')
            if self.accompagnateur and self.programmation_soiree_unesp_invite:
                liste.append('sortie_unesp_invite')
        if self.programmation_soiree_interconsulaire:
            liste.append('sortie_8_mai_membre')
            if self.accompagnateur and \
               self.programmation_soiree_interconsulaire_invite:
                liste.append('sortie_8_mai_invite')
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

    def get_total_categorie(self, cat):
        total = 0
        for ligne in self.get_facture():
            if ligne.infos_montant.categorie == cat:
                total += ligne.total()
        return total

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

    def get_jeton(self):
        return self.invitation.enveloppe.jeton

    def preremplir(self):
        etablissement = self.get_etablissement()
        self.adresse = etablissement.nom + "\n" + etablissement.adresse
        self.ville = etablissement.ville
        self.code_postal = etablissement.code_postal
        self.pays = etablissement.pays.nom
        self.telephone = etablissement.telephone
        self.courriel = self.invitation.courriel
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

    def prise_en_charge_hebergement_possible(self):
        return (self.est_pour_mandate() and self.est_pour_sud() and
                self.get_etablissement().statut in ("T", "A"))

    def prise_en_charge_transport_possible(self):
        return (
            self.est_pour_mandate() and self.est_pour_sud() and
            self.get_etablissement().statut == "T"
        )

    def paiement_paypal_ok(self):
        return self.paiementpaypal_set.filter(
            Q(ipn_valide=True) | Q(pdt_valide=True)
        ).count()

    def paiement_paypal_total(self):
        paiements = self.paiementpaypal_set.filter(
            Q(ipn_valide=True) | Q(pdt_valide=True)
        )
        return sum(
            paiement.montant for paiement in paiements
            if (paiement.montant and
                paiement.statut in PaiementPaypal.STATUS_ACCEPTED)
        )

    def numeros_confirmation_paypal(self):
        return u', '.join([
            paiement.numero_transaction
            for paiement in self.paiementpaypal_set.all()
            if (paiement.montant and
                paiement.statut in PaiementPaypal.STATUS_ACCEPTED)
        ])

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

paypal_signal = Signal()


class PDTInvalide(Exception):
    pass


class PaiementPaypal(models.Model):
    STATUS_ACCEPTED = ['Processed', 'Completed']

    date_heure = models.DateTimeField(
        verbose_name=u'Date et heure du paiement', null=True
    )
    montant = models.FloatField(null=True)
    devise = models.CharField(max_length=32, null=True)
    numero_transaction = models.CharField(
        max_length=250, db_index=True, unique=True
    )
    statut = models.CharField(max_length=64, null=True)
    raison_attente = models.CharField(max_length=128, null=True)
    ipn_post_data = models.TextField(null=True)
    pdt_reponse = models.TextField(null=True)
    inscription = models.ForeignKey(Inscription, null=True)
    ipn_valide = models.BooleanField(default=False)
    pdt_valide = models.BooleanField(default=False)

    def est_complet(self):
        return self.est_valide() and self.statut in self.STATUS_ACCEPTED

    def est_valide(self):
        return self.ipn_valide or self.pdt_valide

    def notifier(self):
        if self.ipn_valide or self.pdt_valide:
            paypal_signal.send_robust(self)

    def verifier_pdt(self):
        postback_dict = dict(
            cmd="_notify-synch", at=settings.PAYPAL_PDT_TOKEN,
            tx=self.numero_transaction
        )
        postback_params = urlencode(postback_dict)
        reponse = urllib2.urlopen(settings.PAYPAL_URL, postback_params).read()
        self.pdt_reponse = reponse
        lignes = reponse.split('\n')
        self.pdt_valide = unquote_plus(lignes[0]) == 'SUCCESS'
        if not self.pdt_valide:
            raise PDTInvalide
        d = {}
        del lignes[0]
        for ligne in lignes:
            ligne = unquote_plus(ligne)
            if "=" in ligne:
                key, value = ligne.split("=")
                d[key] = value
        return d

    def verifier_ipn(self, request):
        query = getattr(request, request.method).urlencode()
        reponse = urllib2.urlopen(
            settings.PAYPAL_URL, "cmd=_notify-validate&%s" % query
        ).read()
        self.ipn_valide = reponse == 'VERIFIED'
