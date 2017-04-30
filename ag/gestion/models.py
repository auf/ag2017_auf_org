# -*- encoding: utf-8 -*-
import datetime
import os
import unicodedata
import collections
import exceptions

from auf.django.permissions import Role
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.db.models import (
    Model, PROTECT, DecimalField,
    CharField, DateField, EmailField, TextField, IntegerField,
    BooleanField, TimeField, DateTimeField, NullBooleanField,
    ForeignKey, ManyToManyField, OneToOneField, FileField, Manager, Q)
from django.db.models.aggregates import Sum, Max, Min, Count
from django.dispatch.dispatcher import Signal
from django.utils.datastructures import SortedDict

from ag import reference
from ag.core import models as core
from ag.gestion import consts
from ag.gestion.consts import *
from ag.gestion.participants_queryset import ParticipantsQuerySet
from ag.inscription.models import (
    Inscription,
    RenseignementsPersonnels,
    Paiement as PaiementNamedTuple,
    Forfait)
from ag.reference.models import Etablissement, Region, Pays, Implantation, \
    CODE_ASSOCIE, CODE_RESEAU, CODE_TITULAIRE

__all__ = ('Participant',
           'nouveau_participant',
           'ParticipationActivite',
           'Invite',
           'get_donnees_hotels',
           'get_nombre_votants_par_region',
           'get_inscriptions_par_mois',
           'PointDeSuivi',
           'Hotel',
           'Fichier',
           'VolGroupe',
           'InfosVol',
           'Activite',
           'AGRole',
           'ReservationChambre',
           'TypeFrais',
           'Paiement',
           'ActiviteScientifique',
           'Fonction',
           'TypeInstitution',
           'Chambre',
           'InscriptionWeb',
           'Invitation',
           'Institution',
           'CategorieFonction',
           'InfosDepartArrivee',
           'infos_depart_arrivee_from_infos_vols',
           'EMPTY_ARRIVEE', 'EMPTY_DEPART',
           'EN_COURS',
           )


class TypeInstitution(core.TableReferenceOrdonnee):
    class Meta:
        verbose_name = u"Type d'institution"
        verbose_name_plural = u"Types d'institutions"
        ordering = ['ordre']

    @property
    def est_etablissement(self):
        return self.code == consts.TYPE_INST_ETABLISSEMENT

    @property
    def est_aucune(self):
        return self.code == consts.TYPE_INST_AUCUNE


class CategorieFonction(core.TableReference):
    class Meta:
        verbose_name = u"Catégorie fonction participant"
        verbose_name_plural = u"Catégories fonctions participants"


class Fonction(core.TableReferenceOrdonnee):
    class Meta:
        verbose_name = u"Fonction participant"
        verbose_name_plural = u"Fonctions participants"
        ordering = ['ordre']

    categorie = ForeignKey(CategorieFonction)
    type_institution = ForeignKey(TypeInstitution, null=True, blank=True)

    @property
    def repr_etablissement(self):
        return (self.type_institution and
                self.type_institution.code == consts.TYPE_INST_ETABLISSEMENT)

    @property
    def repr_instance_seulement(self):
        return self.code == consts.FONCTION_INSTANCE_SEULEMENT

    @property
    def repr_auf(self):
        return self.code == consts.FONCTION_PERSONNEL_AUF


def get_fonction_repr_universitaire():
    return Fonction.objects.get(code=consts.FONCTION_REPR_UNIVERSITAIRE)


def get_fonction_instance_seulement():
    return Fonction.objects.get(code=consts.FONCTION_INSTANCE_SEULEMENT)


def get_fonction_personnel_auf():
    return Fonction.objects.get(code=consts.FONCTION_PERSONNEL_AUF)


class Institution(Model):
    class Meta:
        ordering = ('nom',)

    nom = CharField(max_length=512, null=False, blank=False)
    type_institution = ForeignKey(TypeInstitution)
    pays = ForeignKey(reference.models.Pays)
    region = ForeignKey(reference.models.Region)

    def __unicode__(self):
        return self.nom


class PointDeSuiviManager(Manager):
    def avec_nombre_participants(self):
        queryset = self.get_queryset().filter(
            Q(participant__desactive=False) |
            Q(participant__isnull=True))
        queryset = queryset.annotate(
            nombre_participants=Count('participant'))
        return queryset


class PointDeSuivi(core.TableReferenceOrdonnee):
    class Meta:
        verbose_name = u"Point de suivi participant"
        verbose_name_plural = u"Points de suivi participants"
        ordering = ['ordre']

    objects = PointDeSuiviManager()


def get_type_chambre_par_code(code):
    return next(
        un_type_chambre
        for un_type_chambre in TYPES_CHAMBRES
        if un_type_chambre['code'] == code
    )


def get_type_chambre_index(code):
    index = TYPES_CHAMBRES.index(get_type_chambre_par_code(code))
    return index


class Hotel(core.TableReference):
    class Meta:
        verbose_name = u"Hôtel"
        verbose_name_plural = u"Hôtels"
    adresse = TextField()
    telephone = CharField(max_length=32, blank=True)
    courriel = EmailField(blank=True)
    cacher_dans_tableau_de_bord = BooleanField(u"Ne pas montrer dans le tableau"
                                               u" de bord", null=False,
                                               blank=False, default=False)

    def get_chambres(self):
        if not hasattr(self, "_chambres"):
            self._chambres = Chambre.objects.filter(hotel=self)
            self._chambres = sorted(
                self._chambres,
                key=lambda x: get_type_chambre_index(x.type_chambre)
            )
        return self._chambres

    def nombre_types_chambres(self):
        return len(self.get_chambres())

    def chambres(self):
        """ Renvoie le nombre de places et le nombre de chambres réservées
        pour cet hôtel.
        """
        if not hasattr(self, "_infos_chambres"):
            self._info_chambres = SortedDict([
                (chambre.type_chambre, {'nb_total': chambre.nb_total or 0})
                for chambre in self.get_chambres()
            ])
            for code_type_chambre, chambre in self._info_chambres.items():
                chambre['nb_reservees'] = \
                    self.nombre_chambres_reservees_par_type(
                        code_type_chambre
                    )
                chambre['nb_restantes'] = \
                    chambre['nb_total'] - chambre['nb_reservees']
                chambre['type_chambre'] = \
                    get_type_chambre_par_code(code_type_chambre)
        return self._info_chambres

    def chambres_reservees(self):
        if not hasattr(self, '_chambres_reservees'):
            self._chambres_reservees = \
                ReservationChambre.objects.filter(participant__hotel=self)
        return self._chambres_reservees

    def nombre_chambres_reservees_par_type(self, type_chambre):
        return sum([c.nombre for c in self.chambres_reservees()
                    if c.type_chambre == type_chambre])

    def nombre_total_chambres_reservees(self):
        return sum([c.nombre for c in self.chambres_reservees()])

    def nombre_chambres_simples_reservees(self):
        return self.nombre_chambres_reservees_par_type(CHAMBRE_SIMPLE)

    def nombre_chambres_doubles_reservees(self):
        return self.nombre_chambres_reservees_par_type(CHAMBRE_DOUBLE)


class Chambre(Model):
    hotel = ForeignKey(Hotel)
    type_chambre = CharField(
        u"Type de chambre", max_length=1,
        choices=TYPE_CHAMBRE_CHOICES
    )
    places = IntegerField()
    nb_total = IntegerField(null=True)
    prix = DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('hotel', 'type_chambre')

    def __unicode__(self):
        types_chambres = dict(TYPE_CHAMBRE_CHOICES)
        return types_chambres[self.type_chambre]


class TypeFrais(core.TableReference):
    REPAS = u"repas"
    NUITEES = u"nuitees"
    TAXI = u"taxi"
    AUTRES_FRAIS = u"autres"

    class Meta:
        verbose_name = u"Type de frais"
        verbose_name_plural = u"Types de frais"
        ordering = ['libelle']


class ActiviteManager(Manager):
    def with_stats(self):
        qs = self.get_queryset()
        base_query = """
            (SELECT count(*) FROM gestion_participationactivite gp
            INNER JOIN gestion_participant p on p.id = gp.participant_id
            WHERE gp.activite_id = gestion_activite.id
              AND p.desactive=0
        """
        qs = qs.extra(select={
            '_nombre_pris_en_charge': (base_query +
                                       " AND p.prise_en_charge_activites=1)"),
            '_nombre_non_pris_en_charge': (base_query + """ AND
                                           p.prise_en_charge_activites=0)"""),
            '_nombre_invites': """
                (SELECT COUNT(*) FROM (gestion_invite i INNER JOIN
                  gestion_participant p on i.participant_id = p.id)
                  INNER JOIN gestion_participationactivite pa ON
                   pa.participant_id = p.id
                WHERE pa.activite_id = gestion_activite.id
                 AND pa.avec_invites = 1)
            """,
        })
        return qs


class Activite(core.TableReference):
    forfait_invite = ForeignKey(Forfait,
                                verbose_name=u"Forfait invité correspondant",
                                null=True, blank=True)
    objects = ActiviteManager()

    class Meta:
        verbose_name = u"Activité"

    def nombre_participants(self):
        if hasattr(self, '_nombre_participants'):
            return self._nombre_participants
        return ParticipationActivite.objects.filter(
            activite=self,
        ).exclude(participant__desactive=True).count()

    def nombre_personnes_total(self):
        """
        Nombre de participants + leurs invités
        """
        return self.nombre_participants() + self.nombre_invites()

    def nombre_pris_en_charge(self):
        if hasattr(self, '_nombre_pris_en_charge'):
            return self._nombre_pris_en_charge
        return ParticipationActivite.objects.filter(
            activite=self, participant__prise_en_charge_activites=True
        ).exclude(participant__desactive=True).count()

    def nombre_non_pris_en_charge(self):
        if hasattr(self, '_nombre_non_pris_en_charge'):
            return self._nombre_non_pris_en_charge
        return ParticipationActivite.objects.filter(activite=self)\
            .exclude(participant__prise_en_charge_activites=True)\
            .exclude(participant__desactive=True).count()

    def nombre_invites(self):
        if hasattr(self, '_nombre_invites'):
            return self._nombre_invites
        return Invite.objects.filter(
            participant__participationactivite__activite=self,
            participant__participationactivite__avec_invites=True
        ).exclude(participant__desactive=True).count()


class ActiviteScientifique(core.TableReference):
    class Meta:
        verbose_name = u"activité scientifique"
        verbose_name_plural = u"activités scientifiques"
        ordering = ['libelle']

    max_participants = IntegerField(u"Nb de places", default=999, null=False,
                                    blank=False)

    def nb_participants(self):
        return Participant.objects.filter(activite_scientifique=self).count()

    def complet(self):
        return self.nb_participants() >= self.max_participants

    def __unicode__(self):
        # noinspection PyTypeChecker
        return self.libelle + (u' ** (COMPLET) **' if self.complet() else u'')


class ParticipationActivite(Model):
    activite = ForeignKey(Activite)
    participant = ForeignKey('Participant')
    avec_invites = BooleanField(default=False)

    class Meta:
        unique_together = ('activite', 'participant')


class ParticipantsManager(Manager):

    def get_queryset(self):
        return ParticipantsQuerySet(self.model)

    def actifs(self):
        return self.get_queryset().actifs()

    def sql_expr(self, *args, **kwargs):
        return self.get_queryset().sql_expr(*args, **kwargs)

    def sql_filter(self, *args, **kwargs):
        return self.get_queryset().sql_filter(*args, **kwargs)

    def sql_extra_fields(self, *args):
        return self.get_queryset().sql_extra_fields(*args)

    def avec_region_vote(self):
        return self.get_queryset().avec_region_vote()

    def filter_region_vote(self, code_region_vote):
        return self.get_queryset().filter_region_vote(code_region_vote)

    def represente_etablissement(self):
        return self.get_queryset().represente_etablissement()

    def represente_autre_institution(self):
        return self.get_queryset().represente_autre_institution()


class ParticipantsActifsManager(ParticipantsManager):

    def get_queryset(self):
        return super(ParticipantsActifsManager, self).get_queryset().actifs()

nouveau_participant = Signal()


EN_COURS = 'E'
COMPLETE = 'C'


def find_vol_arrivee_ag(infos, villes_possibles,
                        ville_ag):
    infos = [i for i in infos if i.ville_arrivee.upper() in villes_possibles
             and i.ville_depart.upper() != ville_ag]
    if len(infos) == 0:
        return None
    elif len(infos) > 1:
        return [i for i in infos
                if i.ville_arrivee.upper() == ville_ag][0]
    else:
        return infos[0]


def find_vol_depart_ag(infos, villes_possibles, ville_ag):
    # on traite le cas où le participant arrive dans ville ag en faisant
    # escale dans une ville d'arrivee possible et repart directement
    # de cette dernière ville
    infos = [i for i in infos if i.ville_depart.upper() in villes_possibles and
             i.ville_arrivee.upper() != ville_ag]
    if len(infos) == 0:
        return None
    elif len(infos) > 1:
        return [i for i in infos
                if i.ville_depart.upper() == ville_ag][0]
    else:
        return infos[0]


class Participant(RenseignementsPersonnels):
    INSTANCES_AUF = (
        (consts.CA, u"Conseil d'administration"),
        (consts.CS, u"Conseil scientifique"),
    )

    MEMBRE_CA_REPRESENTE = (
        ("E", u"Établissement"),
        ("G", u"Gouvernement"),
    )
    MODALITE_VERSEMENT_FRAIS_SEJOUR_CHOICES = (
        ('A', u"Lors de votre enregistrement à l'assemblée à Marrakech"),
        ('I', u"Au bureau AUF le plus proche"),
        ('V', u"Par virement bancaire")
    )
    IMPUTATION_CHOICES = (
        ('A0394DRI017B3', 'A0394DRI017B3'),
        ('A0394DRI016A3', 'A0394DRI016A3'),
        ('S0255DRI017E1', 'S0255DRI017E1'),
        ('S0256DRI017E1', 'S0256DRI017E1'),
        ('A0394MGP017B1', 'A0394MGP017B1'),
    )

    # référence à l'inscription effectuée par le web, si applicable
    inscription = OneToOneField(Inscription, null=True)
    # utiliser l'adresse GDE comme adresse du participant
    utiliser_adresse_gde = BooleanField(
        u"Utiliser adresse GDE pour la facturation", default=False)
    notes = TextField(blank=True)
    notes_statut = TextField(blank=True)
    # desactivé
    desactive = BooleanField(u"Désactivé", default=False)
    # suivi
    suivi = ManyToManyField(PointDeSuivi)

    ##################################################
    fonction = ForeignKey(Fonction, null=True, blank=True, on_delete=PROTECT)
    institution = ForeignKey(Institution, null=True, blank=True,
                             on_delete=PROTECT)
    instance_auf = CharField(
        u"Instance de l'AUF", max_length=1, choices=INSTANCES_AUF,
        null=True, blank=True)
    membre_ca_represente = CharField(
        u"Ce membre du CA représente", max_length=1,
        choices=MEMBRE_CA_REPRESENTE, null=True, blank=True)
    implantation = ForeignKey(Implantation, null=True, blank=True,
                              on_delete=PROTECT)
    ###################################################

    etablissement = ForeignKey(
        Etablissement, null=True, verbose_name=u"Établissement",
        db_constraint=False)
    numero_facture = IntegerField(u"Numéro de facture", null=True)
    date_facturation = DateField(u"Date de facturation", null=True, blank=True)
    facturation_validee = BooleanField(u"Facturation validée", default=False)
    notes_facturation = TextField(blank=True)
    prise_en_charge_inscription = BooleanField(
        u"Prise en charge frais d'inscription", default=False
    )
    prise_en_charge_transport = NullBooleanField(u"Prise en charge transport")
    prise_en_charge_sejour = NullBooleanField(u"Prise en charge séjour")
    prise_en_charge_activites = BooleanField(
        u"Prise en charge activités", default=False
    )
    imputation = CharField(
        max_length=32, choices=IMPUTATION_CHOICES, blank=True)
    # séjour
    modalite_versement_frais_sejour = CharField(
        u"Modalité de versement",
        max_length=1,
        choices=MODALITE_VERSEMENT_FRAIS_SEJOUR_CHOICES,
        blank=True)
    # transport
    transport_organise_par_auf = BooleanField(u"Transport organisé par l'AUF",
                                              default=False)
    statut_dossier_transport = CharField(
        u"Statut dossier", max_length=1,
        choices=((EN_COURS, u"En cours"), (COMPLETE, u"Complété")), blank=True
    )
    modalite_retrait_billet = CharField(
        u"Modalité de retrait du billet",
        choices=(
            (BUREAU_REGION,
             u"Vos billets vous seront transmis par l'AUF"),
            (COMPTOIR_COMPAGNIE,
             u'Vos billets seront disponibles au '
             u'comptoir de la compagnie aérienne'),
        ),
        max_length=1, blank=True)
    numero_dossier_transport = CharField(u"numéro de dossier", max_length=32,
                                         blank=True)
    notes_transport = TextField(u"Notes", blank=True)
    remarques_transport = TextField(
        u"Remarques reprises sur itinéraire", blank=True
    )
    vol_groupe = ForeignKey("VolGroupe", null=True, blank=True,
                            on_delete=PROTECT)
    # hébergement
    reservation_hotel_par_auf = BooleanField(u"réservation d'un hôtel",
                                             default=False)
    notes_hebergement = TextField(u"notes hébergement", blank=True)
    hotel = ForeignKey(Hotel, null=True, on_delete=PROTECT)
    # activités (excursions, soirées etc.)
    activites = ManyToManyField(Activite, through='ParticipationActivite')
    activite_scientifique = ForeignKey(ActiviteScientifique, blank=True,
                                       null=True)
    forfaits = ManyToManyField(Forfait)

    commentaires = TextField(blank=True, null=True)

    candidat_a = ForeignKey('elections.Election', blank=True, null=True,
                            on_delete=PROTECT)
    suppleant_de = OneToOneField(
        "self", blank=True, null=True,
        limit_choices_to={'candidat_a__code': consts.ELEC_CA},
        related_name='suppleant',
        on_delete=PROTECT)
    candidat_libre = BooleanField(u"libre", default=False)
    candidat_statut = CharField(max_length=16, choices=consts.STATUTS_CANDIDATS,
                                default=consts.DANS_LA_COURSE)

    last_modified = DateTimeField(auto_now=True, null=True)

    objects = ParticipantsManager()
    actifs = ParticipantsActifsManager()

    def __init__(self, *args, **kwargs):
        super(Participant, self).__init__(*args, **kwargs)
        self._facture = None
        self._reservations = None

    def get_moyens_paiement_display(self):
        moyens = set()
        for paiement in self.paiement_set.all():
            moyens.add(paiement.moyen)
        return u",".join(moyens)

    def candidatures_possibles(self):
        result = set()
        if self.etablissement:
            if (self.etablissement.statut == CODE_TITULAIRE):
                result.update({ELEC_PRES, ELEC_CA})
            if self.etablissement.qualite == CODE_RESEAU:
                result.add(ELEC_CASS_RES)
            if self.etablissement.statut == CODE_TITULAIRE:
                result.add(ELEC_CASS_TIT)
            if self.etablissement.statut == CODE_ASSOCIE:
                result.add(ELEC_CASS_ASS)
        return frozenset(result)

    def get_suppleant(self):
        try:
            return self.suppleant
        except exceptions.AttributeError:
            return None

    def get_nom_suppleant(self):
        suppleant = self.get_suppleant()
        return suppleant.get_nom_complet() if suppleant else u""

    @property
    def represente_etablissement(self):
        return self.fonction and self.fonction.type_institution and \
               self.fonction.type_institution.est_etablissement

    @property
    def represente_instance_seulement(self):
        return (self.fonction and
                self.fonction.code == consts.FONCTION_INSTANCE_SEULEMENT)

    @property
    def est_personnel_auf(self):
        return (self.fonction and
                self.fonction.code == consts.FONCTION_PERSONNEL_AUF)

    @property
    def numero(self):
        if self.inscription:
            return self.inscription.numero
        else:
            return 'B%04d' % self.id

    def get_noms_invites(self):
        return [i.nom_complet for i in self.invite_set.all()]

    def get_reservations(self):
        """

        :return:  collections.Iterable[ReservationChambre]
        """
        if self._reservations is None:
            self._reservations = self.reservationchambre_set.all()
        return self._reservations

    # noinspection PyTypeChecker
    def get_nombre_chambres(self, type_chambre):
        """ Renvoie le nombre total de réservations du type de chambre indiqué
        """
        reservations = [r for r in self.get_reservations()
                        if r.type_chambre == type_chambre]
        return reservations[0].nombre if len(reservations) else 0

    # noinspection PyTypeChecker
    def get_nombre_chambres_total(self):
        """ Renvoie le nombre total de chambres réservées
        """
        return sum([r.nombre for r in self.get_reservations()])
        # aggregate = self.reservationchambre_set.all().aggregate(Sum('nombre'))
        # # rappel: aggregate retourne un dict comme { 'nombre_sum': 123 }
        # return aggregate.items()[0][1]

    def est_delinquant(self):
        """ Le participant provient-il d'un établissement qui n'est pas à
        jour de ses cotisations ?
        """
        if hasattr(self, 'delinquant'):
            return self.delinquant
        else:
            return self.represente_etablissement \
                and core.EtablissementDelinquant.objects.filter(
                    id=self.etablissement_id
                ).exists()

    def generer_numero_facture(self):
        """
        Génère un numéro de facture: Il y a un compteur pour les
        participants ne provenant pas d'un établissement et un compteur pour
        chaque établissement
        """
        if not self.numero_facture:
            if self.represente_etablissement:
                qs = Participant.objects\
                    .represente_etablissement()\
                    .filter(etablissement=self.etablissement)
            else:
                qs = Participant.objects.represente_autre_institution()
            numero_max = qs.aggregate(max=Max('numero_facture'))['max']
            self.numero_facture = (numero_max or 0) + 1
            self.date_facturation = datetime.datetime.now().date()

    def nombre_invites(self):
        """ Retourne le nombre total d'invités
        """
        return self.invite_set.count()

    def reserver_chambres(self, type_chambre, nombre):
        """ Réserve le nombre de chambres du type demandé
        """
        if nombre:
            try:
                reservation = ReservationChambre.objects.get(
                    participant=self,
                    type_chambre=type_chambre)
            except ReservationChambre.DoesNotExist:
                reservation = ReservationChambre(
                    participant=self,
                    type_chambre=type_chambre)
            reservation.nombre = nombre
            reservation.save()
        else:
            try:
                ReservationChambre.objects.get(
                    participant=self,
                    type_chambre=type_chambre).delete()
            except ReservationChambre.DoesNotExist:
                pass

    def chambres_reservees(self):
        """ Renvoie les informations de réservations de chambres par type
        (utilisée par les templates)
        """
        result = []
        for type_ in TYPES_CHAMBRES:
            nombre = self.get_nombre_chambres(type_['code'])
            if nombre:
                result.append({'type': type_, 'nombre': nombre})
        return result

    def nom_institution(self):
        """
        Renvoie le nom de l'institution à laquelle appartient le participant
        """
        if self.represente_etablissement:
            return self.etablissement.nom if self.etablissement_id else u"???"
        elif self.represente_instance_seulement:
            nom = u"{} AUF seulement".format(self.get_instance_auf_display())
            if self.instance_auf == 'A':
                nom += u"({})".format(self.get_membre_ca_represente_display())
            return nom
        elif self.est_personnel_auf:
            return u"AUF ({})".format(self.implantation.nom) \
                if self.implantation_id else u"???"
        elif self.institution_id:
            return self.institution.nom
        else:
            return u"N/A"

    def inscrire_a_activite(self, activite, avec_invites=False):
        """ Permet d'inscrire le participant à une activité """
        try:
            participation = ParticipationActivite.objects.get(
                participant=self, activite=activite)
        except ParticipationActivite.DoesNotExist:
            participation = ParticipationActivite(participant=self,
                                                  activite=activite)
        participation.avec_invites = avec_invites
        if activite.forfait_invite:
            if avec_invites:
                self.forfaits.add(activite.forfait_invite)
            else:
                self.forfaits.remove(activite.forfait_invite)
        participation.save()

    def desinscrire_d_activite(self, activite):
        """ Permet de désinscrire le participant à une activité """
        try:
            ParticipationActivite.objects.get(
                participant=self, activite=activite).delete()
            if activite.forfait_invite:
                self.forfaits.remove(activite.forfait_invite)
        except ParticipationActivite.DoesNotExist:
            pass

    def get_participation_activite(self, activite):
        """ Le participant est-il inscrit à une activité  ? """
        try:
            return ParticipationActivite.objects.get(
                participant=self, activite=activite)
        except ParticipationActivite.DoesNotExist:
            return None

    def is_participe_activite(self, code_activite):
        return any(pa for pa in self.participationactivite_set.all()
                   if pa.activite.code == code_activite)

    def is_invite_participe_activite(self, code_activite):
        return any(pa for pa in self.participationactivite_set.all()
                   if pa.activite.code == code_activite and  pa.avec_invites)

    def set_frais(self, code_frais, quantite, montant):
        if montant:
            try:
                frais = Frais.objects.get(
                    participant=self, type_frais__code=code_frais
                )
            except Frais.DoesNotExist:
                type_frais = TypeFrais.objects.get(code=code_frais)
                frais = Frais(participant=self, type_frais=type_frais)
            frais.montant = montant
            frais.quantite = quantite
            frais.save()
        else:
            Frais.objects.filter(
                participant=self, type_frais__code=code_frais
            ).delete()

    def get_frais(self, code_frais):
        try:
            frais = Frais.objects.get(
                participant=self, type_frais__code=code_frais
            )
        except Frais.DoesNotExist:
            return None
        return frais

    def get_all_frais(self):
        if not hasattr(self, '_frais'):
            self._frais = self.frais_set.select_related('type_frais').all()
        return self._frais

    def _set_infos_depart_arrivee(self, type_, date, heure, numero_vol,
                                  compagnie, ville):
        try:
            infos = InfosVol.objects.get(participant=self, type_infos=type_)
        except InfosVol.DoesNotExist:
            infos = InfosVol(participant=self, type_infos=type_)
        if type_ == ARRIVEE_SEULEMENT:
            infos.date_arrivee = date
            infos.heure_arrivee = heure
            infos.ville_arrivee = ville
        else:
            assert type_ == DEPART_SEULEMENT
            infos.date_depart = date
            infos.heure_depart = heure
            infos.ville_depart = ville
        infos.numero_vol = numero_vol
        infos.compagnie = compagnie
        infos.save()

    def set_infos_depart_arrivee(self, inscription):
        if inscription.arrivee_date:
            self.set_infos_arrivee(inscription.arrivee_date,
                                   inscription.arrivee_heure,
                                   inscription.arrivee_vol,
                                   inscription.arrivee_compagnie or u"",
                                   inscription.arrivee_a)
        if inscription.depart_date:
            self.set_infos_depart(inscription.depart_date,
                                  inscription.depart_heure,
                                  inscription.depart_vol,
                                  inscription.depart_compagnie or u"",
                                  inscription.depart_de)

    def set_infos_depart(self, date, heure, numero_vol, compagnie,
                         ville):
        """ Permet d'indiquer les informations de départ
        pour les participants dont le transport n'est pas pris en charge """
        self._set_infos_depart_arrivee(
            DEPART_SEULEMENT, date, heure, numero_vol, compagnie, ville
        )

    def set_infos_arrivee(self, date, heure, numero_vol, compagnie,
                          ville):
        """ Permet d'indiquer les informations d'arrivée
        pour les participants dont le transport n'est pas pris en charge """
        self._set_infos_depart_arrivee(
            ARRIVEE_SEULEMENT, date, heure, numero_vol, compagnie, ville
        )

    def filter_infos_vols(self, **filtr):
        def check(infos_vol):
            for field, val in filtr.iteritems():
                if not getattr(infos_vol, field) == val:
                    return False
            return True

        return [iv for iv in self.infosvol_set.all() if check(iv)]

    def get_infos_depart(self):
        """ Renvoie les informations de départ pour les participants dont le
        transport n'est pas pris en charge
        """
        try:
            return self.filter_infos_vols(type_infos=DEPART_SEULEMENT)[0]
        except IndexError:
            return None

    def get_infos_arrivee(self):
        """ Renvoie les informations d'arrivée pour les participants dont le
        transport n'est pas pris en charge
        """
        try:
            return self.filter_infos_vols(type_infos=ARRIVEE_SEULEMENT)[0]
        except IndexError:
            return None

    def get_vols_depart_arrivee(self):
        villes_upper = [v.upper() for v in consts.AEROPORTS_AG]
        ville_ag = consts.VILLE_AG.upper()
        itineraire = self.itineraire()
        infos_arrivee = find_vol_arrivee_ag(
            itineraire,
            villes_upper, ville_ag)
        infos_depart = find_vol_depart_ag(
            itineraire,
            villes_upper, ville_ag)
        return infos_depart, infos_arrivee

    def get_infos_depart_arrivee(self):
        """Renvoie les informations de départ et d'arrivée pour tout participant
        qu'il soit pris en charge ou non. """
        if self.transport_organise_par_auf:
            infos_depart, infos_arrivee = self.get_vols_depart_arrivee()
        else:
            infos_depart = self.get_infos_depart()
            infos_arrivee = self.get_infos_arrivee()
        return infos_depart_arrivee_from_infos_vols(infos_depart, infos_arrivee)

    def get_infos_depart_arrivee_separes(self):
        """Renvoie les informations de départ et d'arrivée pour tout participant
        qu'il soit pris en charge ou non. """
        if self.transport_organise_par_auf:
            infos_depart, infos_arrivee = self.get_vols_depart_arrivee()
        else:
            infos_depart = self.get_infos_depart()
            infos_arrivee = self.get_infos_arrivee()
        return infos_depart, infos_arrivee

    def has_infos_depart_arrivee(self):
        return is_depart_arrivee_complete(self.get_infos_depart_arrivee())

    def itineraire(self):
        """ Renvoie l'itinéraire d'un participant dont le transport est pris
        en charge.
        """
        infos_vols = []
        if self.vol_groupe_id:
            infos_vols.extend(list(self.vol_groupe.infosvol_set.all()))
        infos_vols.extend(self.filter_infos_vols(type_infos=VOL_ORGANISE))
        infos_vols.sort(
            key=lambda i: (i.date_depart or datetime.date(2016, 1, 1),
                           i.heure_depart or datetime.time(0, 0),
                           i.date_arrivee or datetime.date(2018, 1 ,1),
                           i.heure_arrivee or datetime.time(0, 0)))
        return infos_vols

    def save(self, **kwargs):
        if self.id:
            ancien = Participant.objects.get(pk=self.id)
            if self.facturation_validee:
                if not ancien.facturation_validee:
                    self.generer_numero_facture()
                    facturation_validee.send_robust(self)
            else:
                self.numero_facture = None
                self.date_facturation = None
        self.nom = self.nom.upper()
        super(Participant, self).save(**kwargs)

    def get_adresse_facturation(self):
        utiliser_adresse_gde = self.utiliser_adresse_gde and self.etablissement
        etablissement = self.etablissement
        return {
            'adresse': (
                self.adresse if not utiliser_adresse_gde
                else etablissement.adresse
            ),
            'code_postal': (
                self.code_postal if not utiliser_adresse_gde
                else etablissement.code_postal
            ),
            'ville': (
                self.ville if not utiliser_adresse_gde
                else etablissement.ville
            ),
            'pays': (
                self.pays if not utiliser_adresse_gde
                else etablissement.pays.nom
            ),
            'telephone': (
                self.telephone if not utiliser_adresse_gde
                else etablissement.telephone
            ),
            'telecopieur': (
                self.telecopieur if not utiliser_adresse_gde
                else etablissement.fax
            ),
        }

    def get_region(self):
        if self.represente_etablissement:
            return self.etablissement.region
        elif self.est_personnel_auf:
            return self.implantation.region if self.implantation else u""
        elif not self.represente_instance_seulement:
            return self.institution and self.institution.region
        else:
            return None

    def get_region_nom(self):
        region = self.get_region()
        return region.nom if region else u""

    def get_region_id(self):
        region = self.get_region()
        return region.id if region else None

    def get_region_code(self):
        region = self.get_region()
        return region.code if region else u""

    def get_nom_bureau_regional(self):
        return self.get_region().implantation_bureau.nom

    def get_nom_prenom(self):
        return self.nom.upper() + u", " + self.prenom

    def get_nom_prenom_sans_accents(self):
        return strip_accents(self.nom.upper() + u", " + self.prenom)

    def get_nom_complet(self):
        return u'{0} {1}'.format(self.get_genre_display(),
                                 self.get_nom_prenom())

    # noinspection PyTypeChecker
    def get_prenom_nom_poste(self):
        result = self.prenom + u" " + self.nom.upper()
        if self.poste:
            result += u", " + self.poste
        return result

    @staticmethod
    def get_prise_en_charge_text(value, value_demande):
        if value is None:
            text = u"À traiter"
        elif value:
            text = u"Acceptée"
        else:
            text = u"Refusée"
        if value_demande:
            text += u" (demandée)"
        return text

    def get_prise_en_charge_transport_text(self):
        return self.get_prise_en_charge_text(
            self.prise_en_charge_transport,
            self.inscription and self.inscription.prise_en_charge_transport)

    def get_prise_en_charge_sejour_text(self):
        return self.get_prise_en_charge_text(
            self.prise_en_charge_sejour, self.inscription
            and self.inscription.prise_en_charge_hebergement)

    def get_paiement_string(self):
        # todo: voir avec mc ce qu'on met dans la colonne paiement de la liste
        # display = u""
        # if self.accompte:
        #     display += u', paiement : ' + unicode(self.accompte) + u'€'
        # if self.paiement == 'CB' and self.inscription:
        #     display += self.inscription.statut_paypal_text()
        return self.total_deja_paye

    def get_etablissement_sud(self):
        return self.etablissement and self.etablissement.pays.sud

    def get_region_vote_string(self):
        return REGIONS_VOTANTS_DICT[self.region_vote]

    @property
    def total_deja_paye(self):
        return getattr(self, 'total_deja_paye_sql',
                       sum(p.montant for p in self.get_paiements()))

    def a_televerse_passeport(self):
        return any((f for f in self.fichier_set.all() if f.type_fichier == 1))

    def get_paiements(self):
        paiements = [PaiementNamedTuple(
            date=p.date, moyen=p.moyen, ref_paiement=p.ref,
            montant=p.montant_euros, implantation=p.implantation.nom_court,
        ) for p in self.paiement_set.all()]
        if self.inscription:
            paiements.extend(self.inscription.get_paiements())
        return sorted(paiements, key=lambda pm: pm.date)

    def a_forfait(self, code):
        return code in [f.code for f in self.forfaits.all()]

    def ajouter_forfait(self, code):
        self.forfaits.add(Forfait.objects.get(code=code))

    # def get_arrivee(self, ville):
    #     if not self.prise_en_charge_transport:
    #         infos_arrivee = self.get_infos_arrivee()
    #     elif self.vol_groupe:
    #

    def get_region_vote(self):
        if hasattr(self, 'region_vote'):
            return self.region_vote
        elif self.inscription.invitation.pour_mandate:
                return consts.REGION_AUF_REGION_VOTANTS[self.get_region().code]
        else:
            return None

    def get_region_vote_display(self):
        region_vote = getattr(self, 'region_vote', None)
        if region_vote:
            return REGIONS_VOTANTS_DICT[region_vote]
        else:
            return u""

    def get_fonction_libelle(self):
        return self.fonction.libelle if self.fonction else u"(aucune)"

    # noinspection PyTypeChecker
    def __unicode__(self):
        return u"<Participant: " + self.get_nom_prenom() + \
               u" (" + str(self.id) + u")>"


facturation_validee = Signal()


class Paiement(Model):
    participant = ForeignKey(Participant)
    date = DateField()
    montant_euros = DecimalField(u"Montant (€)", decimal_places=2,
                                 max_digits=10)
    moyen = CharField(u"modalité", max_length=2, choices=PAIEMENT_CHOICES)
    implantation = ForeignKey(Implantation)
    ref = CharField(u"référence", max_length=255)
    montant_devise_locale = DecimalField(
        u'paiement en devises locales', blank=True, null=True,
        decimal_places=2, max_digits=16)
    devise_locale = CharField(u'devise paiement', max_length=3,
                              blank=True, null=True)

    def to_paiement_namedtuple(self):
        return PaiementNamedTuple(
            date=self.date,
            montant=self.montant_euros,
            moyen=self.moyen,
            implantation=self.implantation.nom_court,
            ref_paiement=self.ref,
        )


class Invite(Model):
    """ Représente un invité d'un participant
    """
    genre = CharField(
        max_length=1, choices=RenseignementsPersonnels.GENRE_CHOICES
    )
    nom = CharField('nom', max_length=100)
    prenom = CharField('prénom(s)', max_length=100)
    participant = ForeignKey(Participant)

    @property
    def nom_complet(self):
        return u'{0} {1} {2}'.format(self.get_genre_display(), self.nom,
                                     self.prenom)

    def __unicode__(self):
        return self.nom_complet


class ReservationChambre(Model):
    """ Réservation de chambre pour un participant
    """
    participant = ForeignKey(Participant)
    type_chambre = CharField(
        max_length=1, choices=TYPE_CHAMBRE_CHOICES
    )
    nombre = IntegerField()

    class Meta:
        unique_together = ('participant', 'type_chambre')


class VolGroupeManager(Manager):
    def get_queryset(self):
        return super(VolGroupeManager, self).get_queryset()\
            .extra(select={'nb_participants': """
                (SELECT count(*) from gestion_participant
                 WHERE gestion_participant.vol_groupe_id =
                 gestion_volgroupe.id AND gestion_participant.desactive=False)
            """})


class VolGroupe(Model):
    """ Représente un vol groupé
    """
    nom = CharField(max_length=256, null=False, blank=False)
    nombre_de_sieges = IntegerField(null=True, blank=True)
    objects = VolGroupeManager()

    class Meta:
        ordering = ['nom']

    def get_nb_participants(self):
        if not hasattr(self, 'nb_participants'):
            self.nb_participants = self.get_participants().count()
        return self.nb_participants

    def est_utilise(self):
        return self.get_nb_participants() > 0

    def __unicode__(self):
        return self.nom + u" (%s/%s)" % (self.get_nb_participants(),
                                         self.nombre_de_sieges)

    def get_participants(self):
        return Participant.objects.filter(vol_groupe=self)\
            .select_related('etablissement', 'etablissement__region')\
            .filter(desactive=False)\
            .order_by('nom', 'prenom')

    def get_prix_total(self):
        vols = self.infosvol_set.all()
        return sum([vol.prix or 0 for vol in vols])


class InfosVol(Model):
    """ Informations de vol, utilisé à la fois pour les trajets organisés,
    pour les informations de départ et d'arrivée des participants non
    pris en charge, ainsi que pour les vols groupés.
    """
    TYPE_VOL = (
        (ARRIVEE_SEULEMENT, u'Arrivée seulement'),
        (DEPART_SEULEMENT, u'Départ seulement'),
        (VOL_ORGANISE, u"Vol organisé par l'AUF"),
        (VOL_GROUPE, u"Vol groupé"),
    )

    class Meta:
        ordering = ['date_depart', 'heure_depart']

    participant = ForeignKey(Participant, null=True)
    vol_groupe = ForeignKey(VolGroupe, null=True)
    ville_depart = CharField(u"Ville de départ", max_length=128, blank=True)
    date_depart = DateField(u"Date de départ", null=True, blank=True)
    heure_depart = TimeField(u"Heure de départ", null=True, blank=True)
    ville_arrivee = CharField(u"Ville d'arrivée", max_length=128, blank=True)
    date_arrivee = DateField(u"Date d'arrivée", null=True, blank=True)
    heure_arrivee = TimeField(u"Heure d'arrivée", null=True, blank=True)
    numero_vol = CharField(u"N° vol", max_length=16, blank=True)
    compagnie = CharField(max_length=64, blank=True)
    prix = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_infos = IntegerField(choices=TYPE_VOL, default=VOL_ORGANISE)

    def participants(self):
        if self.type_infos == VOL_GROUPE:
            return list(self.vol_groupe.get_participants())
        else:
            return [self.participant]

    def get_heure_ville_jour(self, arrivees_departs):
        if arrivees_departs == ARRIVEES:
            return self.heure_arrivee, self.ville_arrivee, self.date_arrivee
        else:
            return self.heure_depart, self.ville_depart, self.date_depart

    def __unicode__(self):
        return u"{} {} {} → {} {} {}".format(
            self.compagnie, self.numero_vol, self.ville_depart,
            self.ville_arrivee, self.date_depart, self.heure_depart
        )


class Frais(Model):
    participant = ForeignKey(Participant)
    type_frais = ForeignKey(TypeFrais)
    quantite = IntegerField(u"quantité", default=1)
    montant = DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return (self.quantite or 1) * (self.montant or 0)


FILE_STORAGE = FileSystemStorage(location=settings.PATH_FICHIERS_PARTICIPANTS)


def get_participant_file_path(fichier, filename):
    return os.path.join(str(fichier.participant.id), filename)


class Fichier(Model):
    participant = ForeignKey(Participant)
    fichier = FileField(upload_to=get_participant_file_path,
                        storage=FILE_STORAGE)
    type_fichier = IntegerField(default=0, choices=(
        (0, u"Autres"),
        (1, u"Passeport")
    ))
    cree_le = DateTimeField(u"créé le ", auto_now_add=True)
    cree_par = ForeignKey(User, on_delete=PROTECT, null=True, related_name='+')
    efface_le = DateTimeField(u"effacé le ", null=True)
    efface_par = ForeignKey(
        User, on_delete=PROTECT, null=True, related_name='+')

    def filename(self):
        return os.path.basename(self.fichier.name)


def get_donnees_hotels():
    """
    Renvoie un récapitulatif du nombre de chambres réservées par type de
    chambre, par hôtel et par date
    """
    limites_date = Participant.actifs.aggregate(
        premiere_date=Min('date_arrivee_hotel'),
        derniere_date=Max('date_depart_hotel'))
    premiere_date, derniere_date = \
        limites_date['premiere_date'], limites_date['derniere_date']
    if premiere_date and derniere_date:
        nb_jours = (derniere_date - premiere_date).days
    else:
        nb_jours = 0
    donnees_hotels_par_jour = []
    hotels = Hotel.objects.exclude(cacher_dans_tableau_de_bord=True)\
        .order_by('libelle')
    types_chambres = TYPES_CHAMBRES
    totaux_dict = {}
    for hotel in hotels:
        totaux_dict[hotel.id] = {}

    for date in (
        premiere_date + datetime.timedelta(n) for n in range(nb_jours)
    ):
        donnees_chambres = ReservationChambre.objects \
            .filter(participant__date_arrivee_hotel__lte=date,
                    participant__date_depart_hotel__gt=date,
                    participant__reservation_hotel_par_auf=True,
                    participant__desactive=False) \
            .values('participant__hotel', 'type_chambre') \
            .annotate(total=Sum('nombre'))
        par_hotel_par_type = []
        for hotel in hotels:
            for chambre in hotel.get_chambres():
                code_type_chambre = chambre.type_chambre
                nb_chambres = [
                    donnees_chambre['total']
                    for donnees_chambre in donnees_chambres
                    if donnees_chambre['participant__hotel'] == hotel.id
                    and donnees_chambre['type_chambre'] == code_type_chambre
                ]
                nb_chambres = nb_chambres[0] if nb_chambres else 0
                par_hotel_par_type.append(nb_chambres)
                totaux_dict[hotel.id][code_type_chambre] = \
                    totaux_dict[hotel.id].get(code_type_chambre, 0) + \
                    nb_chambres
        donnees_hotels_par_jour.append((date, par_hotel_par_type))

    totaux = []
    for hotel in hotels:
        for code_type_chambre in hotel.chambres().keys():
            if code_type_chambre in totaux_dict[hotel.id]:
                totaux.append(totaux_dict[hotel.id][code_type_chambre])
            else:
                totaux.append(0)

    return hotels, types_chambres, donnees_hotels_par_jour, totaux


VotantsRegion = collections.namedtuple("VotantsRegion",
                                       ('nom_region', 'nb_titulaires',
                                        'nb_associes',
                                        'nb_total'))


def get_nombre_votants_par_region():
    """
    Renvoie un récapitulatif du nombre de votants par région,
    ainsi que le nombre total de votants
    """
    donnees_votants = []
    total_titulaires = total_associes = 0
    for region in REGIONS_VOTANTS:
        code_region = region[0]
        nom_region = region[1]
        nb_titulaires = Participant.objects.all().titulaires() \
            .count_par_region_vote(code_region)
        nb_associes = Participant.objects.all().associes() \
            .count_par_region_vote(code_region)
        if code_region != 'FR':
            total_titulaires += nb_titulaires
            total_associes += nb_associes
        else:
            nom_region = 'dont ' + nom_region
        donnees_votants.append(VotantsRegion(nom_region, nb_titulaires,
                                             nb_associes,
                                             nb_titulaires + nb_associes))
    return donnees_votants, (total_titulaires, total_associes,
                             total_titulaires + total_associes)


class InscriptionWeb(Inscription):
    class Meta:
        proxy = True
        app_label = 'gestion'
        verbose_name = u'Inscription'
        ordering = ['date_fermeture']


class AGRole(Model, Role):

    TYPES_ROLES = (
        (ROLE_COMPTABLE, u'Comptable'),
        (ROLE_SAI, u'SAI'),
        (ROLE_LECTEUR, u'Lecteur'),
        (ROLE_ADMIN, u'Admin'),
        (ROLE_SEJOUR, u'Séjour')
    )
    user = ForeignKey(User, verbose_name=u'utilisateur', related_name='roles')
    region = ForeignKey(Region, verbose_name=u'Région', null=True, blank=True,
                        db_constraint=False)
    type_role = CharField(u'Type', max_length=1, choices=TYPES_ROLES)

    class Meta:
        verbose_name = u'Rôle utilisateur'
        verbose_name_plural = u'Rôles des utilisateurs'

    # noinspection PyTypeChecker
    def __unicode__(self):
        s = self.get_type_role_display()
        if self.region:
            s += u' ' + self.region.nom
        return s

    def check_participant_region(self, obj):
        if hasattr(obj, 'get_region'):
            return obj.get_region() == self.region
        else:
            return False

    def has_perm(self, perm, obj=None):
        # les admins peuvent toujours tout faire
        if self.type_role == ROLE_ADMIN:
            return True
        # tout le monde peut lire
        if perm == PERM_LECTURE:
            return True
        if (perm, self.type_role) in ALLOWED:
            # si la permission est globale, OK
            if not self.region:
                return True
            else:
                return self.check_participant_region(obj)
        else:
            if (perm, self.type_role) in ALLOWED_MEME_REGION:
                if self.region:
                    return self.check_participant_region(obj)
                else:
                    return False
        return False

    def participant_region_q(self):
        return Q(
            (Q(fonction__type_institution__code=consts.TYPE_INST_ETABLISSEMENT)
             & Q(etablissement__region=self.region))
            | (Q(institution__region=self.region))
            | (Q(fonction__code=consts.FONCTION_PERSONNEL_AUF) &
               Q(implantation__region=self.region)))

    def get_filter_for_perm(self, perm, model):
        if self.type_role == ROLE_ADMIN or perm == PERM_LECTURE:
            return True
        if ((perm, self.type_role) in ALLOWED or
                (   # les lecteurs peuvent modifier les notes de frais et les
                    # fichiers des participants de leur région
                    (perm, self.type_role) in ALLOWED_MEME_REGION
                    and self.region
                )):
            if not self.region:
                return True
            else:
                if model == Participant:
                    return self.participant_region_q()
                elif model == Inscription:
                    return Q(invitation__etablissement__region=self.region)
                else:
                    return False
        else:
            return False


class Invitation(Model):
    etablissement_nom = CharField(max_length=765)
    etablissement_id = IntegerField(primary_key=True)
    etablissement_region_id = IntegerField(null=True, blank=True)
    jeton = CharField(max_length=96)
    enveloppe_id = IntegerField()
    modele_id = IntegerField()
    sud = BooleanField()
    statut = CharField(max_length=3, blank=True)

    class Meta:
        managed = False
        db_table = u'invitations'
        app_label = 'gestion'
        verbose_name = u'Invitation'


def get_inscriptions_par_mois():
    sql = """SELECT MONTH( date_fermeture ), YEAR( date_fermeture ), count( * )
            FROM inscription_inscription
            WHERE fermee = 1
            GROUP BY MONTH( date_fermeture ) , YEAR( date_fermeture )
            ORDER BY MONTH( date_fermeture ) , YEAR( date_fermeture )
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    inscriptions_par_mois = [
        (datetime.date(row[1], row[0], 1), row[2])
        for row in cursor.fetchall()]
    return inscriptions_par_mois


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', unicode(s))
                    if unicodedata.category(c) != 'Mn'))


InfosDepartArrivee = collections.namedtuple(
    'InfosDepartArrivee', ('arrivee_date', 'arrivee_heure', 'arrivee_vol',
                           'arrivee_compagnie', 'arrivee_a',
                           'depart_date', 'depart_heure', 'depart_vol',
                           'depart_compagnie', 'depart_de',
                           ))

EMPTY_ARRIVEE = {
    'arrivee_date': None,
    'arrivee_heure': None,
    'arrivee_compagnie': u"",
    'arrivee_vol': u"",
    'arrivee_a': u"", }

EMPTY_DEPART = {
    'depart_date': None,
    'depart_heure': None,
    'depart_compagnie': u"",
    'depart_vol': u"",
    'depart_de': u"", }


def infos_depart_arrivee_from_infos_vols(infos_depart, infos_arrivee):
    """

    :param infos_depart: Optional[InfosVol]
    :param infos_arrivee: Optional[InfosVol]
    :return: InfosDepartArrivee
    """
    if infos_depart:
        info_depart_dict = {
            'depart_date': infos_depart.date_depart,
            'depart_heure': infos_depart.heure_depart,
            'depart_compagnie': infos_depart.compagnie,
            'depart_vol': infos_depart.numero_vol,
            'depart_de': infos_depart.ville_depart,
        }
    else:
        info_depart_dict = EMPTY_DEPART

    if infos_arrivee:
        info_arrivee_dict = {
            'arrivee_date': infos_arrivee.date_arrivee,
            'arrivee_heure': infos_arrivee.heure_arrivee,
            'arrivee_compagnie': infos_arrivee.compagnie,
            'arrivee_vol': infos_arrivee.numero_vol,
            'arrivee_a': infos_arrivee.ville_arrivee,
        }
    else:
        info_arrivee_dict = EMPTY_ARRIVEE

    infos_dict = info_depart_dict
    infos_dict.update(info_arrivee_dict)
    return InfosDepartArrivee(**infos_dict)


def is_depart_arrivee_complete(infos_depart_arrivee):
    return (infos_depart_arrivee.depart_de and
            infos_depart_arrivee.arrivee_a and
            infos_depart_arrivee.arrivee_date and
            infos_depart_arrivee.depart_date)
