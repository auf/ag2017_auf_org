# -*- encoding: utf-8 -*-
import re

from django.utils.safestring import mark_safe
from django.utils.html import escape
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Div, MultiField, HTML, Submit
from crispy_forms.layout import Field as crispy_Field
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import connection
from django.forms import forms
from django.forms.fields import (
    IntegerField, CharField, TypedChoiceField, ChoiceField, DateField,
    BooleanField, Field, TimeField, FloatField,
    RegexField)
from django.forms.forms import Form

from django.forms.models import (
    ModelForm, ModelChoiceField, ModelMultipleChoiceField,
    inlineformset_factory, BaseInlineFormSet
)
from django.forms.widgets import (
    HiddenInput, Select, TextInput, RadioSelect, DateInput,
    CheckboxSelectMultiple
)

from ag.reference.models import Etablissement, Region
from ag.gestion import transfert_inscription, consts
from ag.gestion.models import *
from ag.gestion.consts import *
from ag.inscription.models import Inscription, montant_str
from django.utils import formats

PEC_ACCEPTEE = 'A'
PEC_REFUSEE = 'R'
PEC_A_TRAITER = 'T'

PRISE_EN_CHARGE_CHOICES = (
    (u'', u'--------'),
    (PEC_ACCEPTEE, u'Acceptée'),
    (PEC_REFUSEE, u'Refusée'),
    (PEC_A_TRAITER, u'À traiter'),
)

AUCUNE_REGION = 'aucune'


def region_choices():
    return (
        (None, u"--------"),
        (AUCUNE_REGION, u'Sans région')
    ) + tuple(
        (region.id, region.nom) for region in Region.objects.all()
    )


class RechercheParticipantForm(Form):
    # noinspection PyTypeChecker
    PROBLEME_CHOICES = [(u'', u'--------'),
                        (u'problematique', u'Tous les problèmes')] + \
                       [(code, probleme['libelle_court'])
                        for code, probleme in PROBLEMES.items()]

    nom = CharField(label=u'Nom', max_length=128, required=False,
                    widget=TextInput(attrs={'size': 80}))
    fonction = ModelChoiceField(
        label=u"Fonction AG", queryset=Fonction.objects.all(),
        required=False
    )
    etablissement = IntegerField(label=u'Établissement',
                                 widget=HiddenInput(attrs={
                                    'id': 'recherche_etablissement_id'}),
                                 required=False)
    etablissement_nom = CharField(
        label=u'Établissement',
        widget=TextInput(
            attrs={'id': 'recherche_etablissement',
                   'class': 'recherche_etablissement_auto',
                   'size': 80}), required=False)
    instance_auf = ChoiceField(
        label=u"Instance de l'AUF", choices=(('', u'------'), ) +
        Participant.INSTANCES_AUF, required=False
    )
    type_institution = ModelChoiceField(
        label=u'Type institution', queryset=TypeInstitution.objects.all(),
        required=False
    )
    suivi = ModelChoiceField(
        label=u'Suivi', queryset=PointDeSuivi.objects.all(), widget=Select,
        required=False)
    prise_en_charge_inscription = ChoiceField(
        label=u"Prise en charge frais d'inscription",
        choices=PRISE_EN_CHARGE_CHOICES,
        required=False
    )
    prise_en_charge_transport = ChoiceField(
        label=u"Prise en charge transport", choices=PRISE_EN_CHARGE_CHOICES,
        required=False
    )
    prise_en_charge_sejour = ChoiceField(
        label=u"Prise en charge séjour", choices=PRISE_EN_CHARGE_CHOICES,
        required=False
    )
    pays = CharField(label=u"Pays", required=False)
    region = ChoiceField(
        label=u"Région", choices=region_choices, required=False
    )
    probleme = ChoiceField(
        label=u"Problématique", choices=PROBLEME_CHOICES,
        required=False
    )
    hotel = ModelChoiceField(label=u"Hôtel", queryset=Hotel.objects.all(),
                             required=False)
    pays_code = CharField(max_length=5, required=False)
    region_vote = CharField(max_length=12, required=False)
    pas_de_solde_a_payer = BooleanField(label=u"Aucun solde à payer",
                                        required=False)
    activite = ModelChoiceField(label=u"Activité",
                                queryset=Activite.objects.all(),
                                required=False)
    statut = ChoiceField(choices=Etablissement.STATUT_CHOICES, required=False)
    desactive = BooleanField(
        label=u"Désactivés", required=False
    )

    def __init__(self, *args, **kwargs):
        super(RechercheParticipantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Fieldset(
                '',
                'nom', 'fonction', 'type_institution', 'etablissement_nom', 'etablissement',
                'instance_auf', 'region', 'pays',
                'prise_en_charge_transport', 'prise_en_charge_sejour', 'hotel',
                'suivi', 'probleme', 'desactive'
            ),
            Div(
                Submit('chercher', 'Chercher', css_class='default'),
                css_class='submit-row'
            )
        )


def require_field(form, cleaned_data, field_name, shown_on_field=None):
    # si le champ contient des données invalides il ne sera pas dans
    # cleaned_data
    if field_name in cleaned_data:
        if cleaned_data[field_name] in validators.EMPTY_VALUES:
            shown_on_field = field_name \
                if not shown_on_field else shown_on_field
            # noinspection PyProtectedMember
            form._errors.setdefault(shown_on_field, form.error_class())\
                .append(Field.default_error_messages['required'])
            del cleaned_data[shown_on_field]
            if shown_on_field != field_name:
                del cleaned_data[field_name]


class GestionModelForm(ModelForm):
    class Meta:
        exclude = ()

    def get_participant(self):
        return self.instance


class RenseignementsPersonnelsForm(GestionModelForm):
    class Meta:
        model = Participant
        fields = (
            'genre', 'nom', 'prenom', 'desactive', 'nationalite',
            'date_naissance', 'courriel', 'poste',
            'etablissement', 'etablissement_nom',
            'adresse', 'ville', 'code_postal',
            'pays', 'telephone', 'telecopieur', 'notes',
            'fonction', 'institution', 'instance_auf', 'implantation',
            'membre_ca_represente',
            'notes_statut')

    etablissement = IntegerField(
        label=u'Établissement',
        widget=HiddenInput(attrs={'id': 'recherche_etablissement_id'}),
        required=False)

    etablissement_nom = CharField(
        label=u'Établissement',
        widget=TextInput(attrs={'id': 'recherche_etablissement',
                                'class': 'recherche_etablissement_auto',
                                'size': 80}), required=False)

    courriel = CharField(
        label=u"Courriel", widget=TextInput(attrs={'size': 64})
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(Div(
            Fieldset(
                u'Identification',
                'genre', crispy_Field('nom', css_class='to-uppercase'),
                'prenom', 'nationalite',
                'courriel', crispy_Field('date_naissance', ),
                css_id='rp_identification',
            ),
            Fieldset(
                u'Coordonnées',
                'adresse', 'ville', 'code_postal',
                'pays', 'telephone', 'telecopieur',
                css_id='rp_coordonees',
            ),  id='col1'),
            Div(
                Fieldset(
                    u'Dossier',
                    'desactive',
                    'notes',
                    css_id='rp_dossier',
                ),
                Fieldset(
                    u'Statut',
                    'notes_statut',
                    css_id='rp_statut',
                ),
                Fieldset(
                    u'Institution représentée',
                    'fonction', 'institution',
                    'etablissement', 'etablissement_nom',
                    'implantation', 'instance_auf',
                    'membre_ca_represente',
                    'poste',
                    css_id='rp_institution',
                ), id='col2'),
            Div(css_class='clear'),
        )
        super(RenseignementsPersonnelsForm, self).__init__(*args, **kwargs)
        if self.instance.etablissement:
            self.initial['etablissement_nom'] = self.instance.etablissement.nom
        self.set_institution_fields_required(True)

    def set_institution_fields_required(self, required):
        self.fields['fonction'].required = True
        self.fields['etablissement'].required = required
        self.fields['etablissement_nom'].required = required
        self.fields['implantation'].required = required

    def is_valid(self):
        """ les champs affichés comme obligatoires ne le sont parfois
        que sous certaines conditions
        """
        self.set_institution_fields_required(False)
        result = super(RenseignementsPersonnelsForm, self).is_valid()
        self.set_institution_fields_required(True)
        return result

    def clean(self):
        cleaned_data = super(RenseignementsPersonnelsForm, self).clean()
        fonction = cleaned_data['fonction']
        champs_institution = {'etablissement', 'institution', 'implantation'}
        champs_obligatoires = set()
        if fonction.repr_etablissement:
            try:
                cleaned_data['etablissement'] = Etablissement.objects.get(
                    pk=cleaned_data['etablissement'])
            except Etablissement.DoesNotExist:
                cleaned_data['etablissement'] = None
            champs_obligatoires.add('etablissement')
        elif fonction.repr_auf:
            champs_obligatoires.add('implantation')
        elif fonction.type_institution:
            champs_obligatoires.add('institution')
        elif fonction.repr_instance_seulement:
            champs_obligatoires.add('instance_auf')
            if cleaned_data.get('instance_auf', None) == consts.CA:
                champs_obligatoires.add('membre_ca_represente')
        for champ in champs_obligatoires:
            if champ == 'etablissement':
                require_field(self, cleaned_data, champ,
                              'etablissement_nom')
            else:
                require_field(self, cleaned_data, champ)
        for champ in champs_institution - champs_obligatoires:
            if champ in cleaned_data:
                del cleaned_data[champ]
        return cleaned_data


class GestionForm(Form):
    def __init__(self, *args, **kwargs):
        participant = kwargs.pop('participant')
        self.participant = participant
        super(GestionForm, self).__init__(*args, **kwargs)

    def get_participant(self):
        return self.participant


class NotesDeFraisForm(GestionForm):
    modalite_versement_frais_sejour = ChoiceField(
        label=u"Modalité de versement des frais",
        choices=Participant.MODALITE_VERSEMENT_FRAIS_SEJOUR_CHOICES,
        required=False)

    def __init__(self, *args, **kwargs):
        super(NotesDeFraisForm, self).__init__(*args, **kwargs)
        participant = self.participant
        self.initial['modalite_versement_frais_sejour']\
            = participant.modalite_versement_frais_sejour
        # un champ pour chaque type de frais
        frais_multifields = []
        self.frais_fields = []
        for type_frais in TypeFrais.objects.all():
            frais = participant.get_frais(type_frais.code)
            montant_field = FloatField(required=False, widget=CurrencyInput(),
                                       localize=True)
            montant_field_name = 'frais_montant_' + type_frais.code
            self.fields[montant_field_name] = montant_field
            self.initial[montant_field_name] = frais.montant if frais else 0
            quantite_field = IntegerField(required=False, min_value=1)
            quantite_field_name = 'frais_quantite_' + type_frais.code
            self.fields[quantite_field_name] = quantite_field
            self.initial[quantite_field_name] = frais.quantite if frais else 1
            self.frais_fields.append(
                (quantite_field_name, montant_field_name, type_frais)
            )
            frais_multifields.append(
                MultiField(type_frais.libelle, quantite_field_name,
                           montant_field_name,
                           template='gestion/frais_field.html')
            )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Frais',
                HTML(u'<table class="frais"><tbody>'),
                Div(*frais_multifields),
                HTML(u"</table></tbody>"),
                'modalite_versement_frais_sejour'
            ),
        )

    def save(self):
        participant = self.participant
        for (quantite_field_name, montant_field_name, type_frais) \
                in self.frais_fields:
            participant.set_frais(
                type_frais.code, self.cleaned_data[quantite_field_name],
                self.cleaned_data[montant_field_name]
            )
        participant.modalite_versement_frais_sejour = \
            self.cleaned_data['modalite_versement_frais_sejour']
        participant.save()


class SejourForm(GestionForm):
    reservation_par_auf = TypedChoiceField(
        coerce=lambda x: bool(int(x)),
        label=u"Réservation par l'AUF",
        choices=(
            (int(False),
             u"Réservation effectuée par le participant lui-même"),
            (int(True),
             u"Réservation effectuée par l'AUF")
        ),
        widget=RadioSelect)

    hotel = ModelChoiceField(
        label=u"Hôtel", queryset=Hotel.objects.all(), required=False,
        widget=RadioSelect()
    )

    date_arrivee = DateField(
        label=u"Date d'arrivée", required=False,
        widget=DateInput(format='%d/%m/%Y')
    )

    date_depart = DateField(
        label=u"Date de départ", required=False,
        widget=DateInput(format='%d/%m/%Y')
    )

    autres_frais = FloatField(label=u'Autres frais', required=False)
    per_diem = FloatField(label=u'Per diem', required=False)
    activite_scientifique = ModelChoiceField(
        label=u'Atelier scientifique', required=False,
        queryset=ActiviteScientifique.objects.all())
    notes_hebergement = CharField(widget=forms.Textarea(), required=False,
                                  label=u'Notes réservation')

    def __init__(self, *args, **kwargs):
        super(SejourForm, self).__init__(*args, **kwargs)
        participant = self.participant
        self.initial['reservation_par_auf'] = \
            int(participant.reservation_hotel_par_auf)
        self.initial['hotel'] = participant.hotel
        self.initial['date_arrivee'] = participant.date_arrivee_hotel
        self.initial['date_depart'] = participant.date_depart_hotel
        self.initial['notes_hebergement'] = participant.notes_hebergement
        self.initial['activite_scientifique'] = \
            participant.activite_scientifique
        # on crée un champ "nombre de réservations" pour chaque type de chambre
        chambre_field_names = []
        self.chambre_fields_by_type = {}
        for type_chambre in TYPES_CHAMBRES:
            code_chambre = type_chambre['code']
            field = IntegerField(
                required=False, label=u'Nb. ' + type_chambre['libelle_plur']
            )
            field_name = 'chambre_' + code_chambre
            self.chambre_fields_by_type[code_chambre] = field_name
            self.fields[field_name] = field
            self.initial[field_name] = \
                participant.get_nombre_chambres(code_chambre)
            chambre_field_names.append(field_name)
        hotel_fields = [
            crispy_Field(
                chambre_field_name, template='gestion/chambre_field.html'
            )
            for chambre_field_name in chambre_field_names
        ]
        hotel_fields += ['notes_hebergement']
        # on crée deux champs pour chaque activité (participant + invités)
        activite_field_containers = []
        activite_field_names = {}
        for activite in Activite.objects.all():
            participant_field = BooleanField(
                label=activite.libelle, required=False
            )
            participant_field_name = 'activite_' + str(activite.pk)
            invite_field = BooleanField(label=u'Avec invités', required=False)
            invite_field_name = 'invite_activite_' + str(activite.pk)
            self.fields[participant_field_name] = participant_field
            self.fields[invite_field_name] = invite_field
            participation = participant.get_participation_activite(activite)
            self.initial[participant_field_name] = bool(participation)
            self.initial[invite_field_name] = bool(participation) \
                and participation.avec_invites
            activite_field_names[activite] = (
                participant_field_name, invite_field_name
            )
            activite_field_containers.append(
                MultiField(u'', participant_field_name, invite_field_name,
                           template='gestion/activite_field.html'))
        self.activite_field_names = activite_field_names
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Hébergement',
                'reservation_par_auf',
                Div(HTML('{% include "gestion/nombre_invites.html" %}')),
                'hotel', 'date_arrivee', 'date_depart',
                Div(*hotel_fields, id='infos_hotel'),
            ),
            Fieldset(
                u'Activités',
                *activite_field_containers
            ),
            Fieldset(
                u'Atelier scientifique',
                'activite_scientifique'
            )
        )

    def is_valid(self):
        self.set_hotel_fields_required(False)
        result = super(SejourForm, self).is_valid()
        self.set_hotel_fields_required(True)
        return result

    def set_hotel_fields_required(self, required):
        self.fields['date_arrivee'].required = required
        self.fields['date_depart'].required = required

    def save(self):
        participant = self.participant
        participant.activite_scientifique = \
            self.cleaned_data['activite_scientifique']
        participant.reservation_hotel_par_auf = \
            self.cleaned_data['reservation_par_auf']
        participant.hotel = self.cleaned_data['hotel']
        participant.date_arrivee_hotel = self.cleaned_data['date_arrivee']
        participant.date_depart_hotel = self.cleaned_data['date_depart']
        participant.notes_hebergement = \
            self.cleaned_data['notes_hebergement']
        for type_chambre, chambre_field \
                in self.chambre_fields_by_type.iteritems():
            participant.reserver_chambres(
                type_chambre, self.cleaned_data[chambre_field]
            )
        for activite in Activite.objects.all():
            participant_field_name, invite_field_name = \
                self.activite_field_names[activite]
            participant_participe = self.cleaned_data[participant_field_name]
            invite_participe = self.cleaned_data[invite_field_name]
            if participant_participe:
                self.participant.inscrire_a_activite(
                    activite, invite_participe
                )
            else:
                self.participant.desinscrire_d_activite(activite)
        participant.save()

    def clean(self):
        cleaned_data = super(SejourForm, self).clean()
        reservation_par_auf = cleaned_data.get('reservation_par_auf')
        hotel = cleaned_data.get('hotel', None)
        if reservation_par_auf and hotel:
            require_field(self, cleaned_data, 'date_arrivee')
            require_field(self, cleaned_data, 'date_depart')
            total_chambres = 0
            for type_chambre, chambre_field \
                    in self.chambre_fields_by_type.iteritems():
                total_chambres += int(cleaned_data.get(chambre_field) or 0)
            if not total_chambres:
                raise ValidationError(
                    u'Indiquez le nombre de chambres à réserver'
                )
        if 'date_arrivee' in cleaned_data \
           and 'date_depart' in cleaned_data:
            date_arrivee = cleaned_data['date_arrivee']
            date_depart = cleaned_data['date_depart']
            if date_arrivee and date_depart:
                if (date_depart - date_arrivee).days < 1:
                    raise ValidationError(u"La date de départ doit être "
                                          u"postérieure à la date d'arrivée")
        return cleaned_data


class SuiviForm(GestionModelForm):
    class Meta:
        model = Participant
        fields = ('suivi', 'commentaires')

    suivi = ModelMultipleChoiceField(
        PointDeSuivi.objects.all(), widget=CheckboxSelectMultiple(),
        required=False
    )


# Affreux hack, mais le seul trouvé pour avoir une virgule comme séparateur
# décimal dans les champs de formulaire
class CurrencyInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value != '' and value is not None:
            try:
                value = formats.number_format(value, 2)
            except (TypeError, ValueError):
                pass
        return super(CurrencyInput, self).render(name, value, attrs)


class CurrencyField(RegexField):
    currencyRe = re.compile(r'^[0-9]*([,.][0-9]{1,2})?$')

    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(
            self.currencyRe, None, None, *args, **kwargs)

    def clean(self, value):
        value = super(CurrencyField, self).clean(value)
        return float(value.replace(',', '.')) if value else None


class VolForm(ModelForm):
    date_arrivee = DateField(label=u"Date d'arrivée", required=False,
                             input_formats=('%d/%m/%Y',),
                             widget=DateInput(format='%d/%m/%Y'))
    date_depart = DateField(label=u"Date de départ", required=False,
                            input_formats=('%d/%m/%Y',),
                            widget=DateInput(format='%d/%m/%Y'))
    prix = CurrencyField(widget=CurrencyInput, required=False)

    class Meta:
        model = InfosVol
        exclude = ('type_infos', 'participant', 'vol_groupe')

    def __init__(self, *args, **kwargs):
        super(VolForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(MultiField(
            u'', 'date_depart', 'heure_depart', 'ville_depart',
            'date_arrivee', 'heure_arrivee', 'ville_arrivee', 'compagnie',
            'numero_vol', 'prix', 'DELETE',
            template='gestion/ligne_vol.html'
        ))
        self.helper.form_tag = False
        self.helper.form_method = 'get'

    def clean(self):
        return dict(
            (k, v.strip().upper() if isinstance(v, basestring) else v)
            for k, v in self.cleaned_data.iteritems()
        )

    def save(self, commit=True):
        instance = super(VolForm, self).save(commit=False)
        instance.type_infos = getattr(self, 'type_infos', VOL_ORGANISE)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class BaseVolFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = InfosVol.objects.filter(type_infos=VOL_ORGANISE)
        super(BaseVolFormset, self).__init__(*args, **kwargs)


VolFormSet = inlineformset_factory(Participant, InfosVol, VolForm,
                                   formset=BaseVolFormset, extra=2)


class TransportFormTop(GestionModelForm):
    class Meta:
        model = Participant
        fields = ('transport_organise_par_auf', 'statut_dossier_transport',
                  'numero_dossier_transport', 'modalite_retrait_billet',
                  'vol_groupe')

    choices = ((False, u"par le participant lui-même"),
               (True, u"par l'AUF"))
    transport_organise_par_auf = TypedChoiceField(
        coerce=lambda x: x == 'True',
        label=u"Transport organisé", choices=choices,
        widget=RadioSelect, required=True)
    vol_groupe = ModelChoiceField(VolGroupe.objects.all(), empty_label=u"Non",
                                  label=u"Vol groupé", required=False)

    def __init__(self, *args, **kwargs):
        super(TransportFormTop, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Organisation',
                'transport_organise_par_auf',
                crispy_Field('statut_dossier_transport',
                             css_class='required'),
                Div(
                    HTML('{% include "gestion/nombre_invites.html" %}'),
                    'numero_dossier_transport', 'modalite_retrait_billet',
                    'vol_groupe', css_class='organise_par_auf'),
            ),
        )
        self.helper.form_tag = False


class TransportFormBottom(GestionModelForm):
    class Meta:
        model = Participant
        fields = ('notes_transport', 'remarques_transport')

    def __init__(self, *args, **kwargs):
        super(TransportFormBottom, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Notes',
                'notes_transport', 'remarques_transport',
                css_class='organise_par_auf'
            ),
        )
        self.helper.form_tag = False
        self.helper.form_method = 'get'  # on n'a pas besoin de tous ces csrf


class ArriveeDepartForm(GestionForm):

    date_arrivee = DateField(
        label=u"Date d'arrivée", required=False,
        input_formats=('%d/%m/%Y',), widget=DateInput(format='%d/%m/%Y'))
    heure_arrivee = TimeField(label=u"Heure d'arrivée", required=False)
    compagnie_arrivee = CharField(label=u"Compagnie arrivée", required=False)
    numero_vol_arrivee = CharField(label=u"No. vol arrivée", required=False)
    ville_arrivee = CharField(label=u"Ville arrivée", required=False)
    date_depart = DateField(
        label=u"Date de départ", required=False,
        input_formats=('%d/%m/%Y',), widget=DateInput(format='%d/%m/%Y'))
    heure_depart = TimeField(label=u"Heure de départ", required=False)
    compagnie_depart = CharField(label=u"Compagnie départ", required=False)
    numero_vol_depart = CharField(label=u"No. vol départ", required=False)
    ville_depart = CharField(label=u"Ville départ", required=False)

    def __init__(self, *args, **kwargs):
        super(ArriveeDepartForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Arrivée',
                'date_arrivee', 'heure_arrivee', 'compagnie_arrivee',
                'numero_vol_arrivee', 'ville_arrivee',
                css_class='organise_par_participant'
            ),
            Fieldset(
                u'Départ',
                'date_depart', 'heure_depart', 'compagnie_depart',
                'numero_vol_depart', 'ville_depart',
                css_class='organise_par_participant'
            ),
        )
        self.helper.form_tag = False
        self.helper.form_method = 'get'  # on n'a pas besoin de tous ces csrf
        infos_depart = self.participant.get_infos_depart()
        if infos_depart:
            self.initial['date_depart'] = infos_depart.date_depart
            self.initial['heure_depart'] = infos_depart.heure_depart
            self.initial['compagnie_depart'] = infos_depart.compagnie
            self.initial['numero_vol_depart'] = infos_depart.numero_vol
            self.initial['ville_depart'] = infos_depart.ville_depart
        infos_arrivee = self.participant.get_infos_arrivee()
        if infos_arrivee:
            self.initial['date_arrivee'] = infos_arrivee.date_arrivee
            self.initial['heure_arrivee'] = infos_arrivee.heure_arrivee
            self.initial['compagnie_arrivee'] = infos_arrivee.compagnie
            self.initial['numero_vol_arrivee'] = infos_arrivee.numero_vol
            self.initial['ville_arrivee'] = \
                infos_arrivee.ville_arrivee

    def save(self):
        participant = self.participant
        participant.set_infos_depart(self.cleaned_data['date_depart'],
                                     self.cleaned_data['heure_depart'],
                                     self.cleaned_data['numero_vol_depart'],
                                     self.cleaned_data['compagnie_depart'],
                                     self.cleaned_data['ville_depart'])
        participant.set_infos_arrivee(self.cleaned_data['date_arrivee'],
                                      self.cleaned_data['heure_arrivee'],
                                      self.cleaned_data['numero_vol_arrivee'],
                                      self.cleaned_data['compagnie_arrivee'],
                                      self.cleaned_data['ville_arrivee'])


class InviteForm(ModelForm):
    class Meta:
        model = Invite
        fields = ('genre', 'nom', 'prenom')

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Fieldset(u'Invité',
                                             'genre', 'nom', 'prenom',
                                             Div('DELETE',
                                                 css_class='hidden-row'),
                                             css_class='invite-fieldset'))


InvitesFormSet = inlineformset_factory(Participant, Invite, form=InviteForm,
                                       extra=1)


class FacturationForm(GestionModelForm):

    class Meta:
        model = Participant
        fields = (
            'prise_en_charge_inscription', 'prise_en_charge_transport',
            'prise_en_charge_sejour',
            'prise_en_charge_activites',
            'facturation_validee', 'date_facturation',
            'imputation', 'notes_facturation', 'forfaits',
        )

        widgets = {
            'forfaits': CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(FacturationForm, self).__init__(*args, **kwargs)
        participant = self.get_participant()
        if not participant.facturation_validee:
            self.fields['date_facturation'].widget = HiddenInput()
        if participant.inscription:
            if participant.inscription.prise_en_charge_hebergement:
                self.fields['prise_en_charge_sejour'].help_text = \
                    u'Prise en charge demandée'
            if participant.inscription.prise_en_charge_transport:
                self.fields['prise_en_charge_transport'].help_text = \
                    u'Prise en charge demandée'
        self.fields['forfaits'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u"Prise en charge", 'prise_en_charge_inscription',
                'prise_en_charge_transport', 'prise_en_charge_sejour',
                'prise_en_charge_activites',
            ),
            Fieldset(
                u"Forfaits", 'forfaits',
            ),
            Fieldset(u"Autres informations", 'facturation_validee',
                     'date_facturation', 'imputation', 'notes_facturation'),
        )


class PaiementForm(ModelForm):
    class Meta:
        model = Paiement
        fields = ('date', 'moyen', 'implantation', 'ref', 'montant_euros',
                  'montant_devise_locale', 'devise_locale')
        field_classes = {
            'montant_euros': CurrencyField,
            'montant_devise_locale': CurrencyField,
        }

    def __init__(self, *args, **kwargs):
        super(PaiementForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            MultiField(u'', 'date', 'moyen', 'implantation', 'ref',
                       'montant_euros', 'montant_devise_locale',
                       'devise_locale', 'DELETE',
                       template='gestion/ligne_paiement.html'))
        self.helper.form_tag = False
        self.helper.form_method = 'get'


PaiementFormset = inlineformset_factory(Participant, Paiement,
                                        form=PaiementForm, extra=1)


class ValidationInscriptionForm(ModelForm):
    class Meta:
        model = Inscription
        exclude = ('invitation', )

    def __init__(self, *args, **kwargs):
        super(ValidationInscriptionForm, self).__init__(*args, **kwargs)
        self.initial['paiement_paypal_total_str'] = \
            montant_str(self.instance.paiement_paypal_total())
        self.fields['paiement_paypal_total_str'].help_text = mark_safe(
            u'Reçu par paypal : ' + u";".join(
                [u"{}-{}-{}".format(p.date, p.montant, escape(p.ref_paiement))
                 for p in self.instance.get_paiements_display()]))
        if self.instance.get_facturer_chambre_double():
            self.initial['facturer_supplement_chambre_double'] = True

    inscription_validee = BooleanField(
        label=(
            u"Valider cette inscription et enregistrer le participant dans "
            u"le système de gestion"
        ), required=False
    )
    accepter_transport = BooleanField(
        label=u"Prise en charge transport acceptée", required=False)
    accepter_hebergement = BooleanField(
        label=u"Prise en charge hébergement acceptée", required=False)
    facturer_supplement_chambre_double = BooleanField(
        label=u"Facturer un supplément pour chambre double", required=False)
    paiement_paypal_total_str = CharField(
        label=u"Total des paiements par paypal", required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    def save(self, commit=True):
        obj = super(ValidationInscriptionForm, self).save(commit)
        if self.cleaned_data['inscription_validee']:
            transfert_inscription.transfere(
                self.instance,
                self.cleaned_data['accepter_transport'],
                self.cleaned_data['accepter_hebergement'],
                self.cleaned_data['facturer_supplement_chambre_double']
            )
        return obj


class AjoutFichierForm(ModelForm):
    class Meta:
        model = Fichier
        exclude = ('participant', 'cree_le', 'cree_par', 'efface_par',
                   'efface_le')


class BaseVolGroupeFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = InfosVol.objects.filter(type_infos=VOL_GROUPE)
        super(BaseVolGroupeFormset, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(BaseVolGroupeFormset, self)._construct_form(i, **kwargs)
        form.type_infos = VOL_GROUPE
        return form


VolGroupeFormSet = inlineformset_factory(VolGroupe, InfosVol, VolForm,
                                         formset=BaseVolGroupeFormset, extra=2)


class VolGroupeForm(ModelForm):
    class Meta:
        model = VolGroupe
        fields = ('nom', 'nombre_de_sieges')

    def __init__(self, *args, **kwargs):
        super(VolGroupeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'nom', 'nombre_de_sieges'
            ),
        )
        self.helper.form_tag = False

ARRIVEES_DEPARTS_CHOICES = ((ARRIVEES, u"Arrivées"),
                            (DEPARTS, u"Départs"))


def villes_vols():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT ville_arrivee as ville FROM gestion_infosvol
        UNION
        SELECT DISTINCT ville_depart as ville FROM gestion_infosvol
        ORDER BY ville
    """)
    return [(row[0], row[0]) for row in cursor.fetchall()]


class FiltresEtatArriveesForm(Form):
    arrivee_depart = ChoiceField(label=u"Arrivées/Départs",
                                 choices=ARRIVEES_DEPARTS_CHOICES,
                                 required=True, widget=HiddenInput)

    def __init__(self, dates=(), *args, **kwargs):
        dates_str = [(date_.strftime('%d/%m/%Y'), date_.strftime('%d/%m/%Y'))
                     for date_ in dates]
        super(FiltresEtatArriveesForm, self).__init__(*args, **kwargs)
        self.fields['ville'] = ChoiceField(choices=villes_vols(), required=True)
        self.fields['jour'] = ChoiceField(
            required=True,
            choices=dates_str)
