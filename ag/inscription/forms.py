# encoding: utf-8
import datetime

from django import forms
from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe

from ag.inscription.models import Inscription
from ag.gestion.montants import (
    infos_montant_par_nom_champ, infos_montant_par_code
)


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription


class AccueilForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ('identite_confirmee', 'conditions_acceptees')

    def __init__(self, *args, **kwargs):
        super(AccueilForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.est_pour_mandate():
            label = (
                u"J'atteste être le représentant dûment délégué par "
                u"la plus haute autorité de mon établissement pour "
                u"participer à la 16e assemblée générale de l'AUF."
            )
        elif self.instance and not self.instance.est_pour_mandate():
            representants = Inscription.objects.filter(
                invitation__pour_mandate=True,
                invitation__etablissement=self.instance.get_etablissement()
            )
            if len(representants) > 0 and representants[0].prenom and \
               representants[0].nom:
                representant = representants[0]
                label = (
                    u"J'atteste m'inscrire à la 16e assemblée générale "
                    u"de l'AUF comme accompagnateur, à la demande de %s %s, "
                    u"représentant mandaté de l'établissement." %
                    (representant.prenom, representant.nom)
                )
            else:
                label = u"J'accompagne le représentant mandaté " \
                        u"de l'établissement"
        self.fields['identite_confirmee'].label = label

    def require_fields(self):
        for name, field in self.fields.iteritems():
            field.required = True


class RenseignementsPersonnelsForm(forms.ModelForm):
    genre = forms.ChoiceField(
        choices=Inscription.GENRE_CHOICES, label='Civilité',
        widget=forms.RadioSelect, required=False
    )
    accompagnateur_genre = forms.ChoiceField(
        choices=Inscription.GENRE_CHOICES, label='Civilité',
        widget=forms.RadioSelect, required=False
    )

    class Meta:
        model = Inscription
        fields = (
            'genre', 'nom', 'prenom', 'nationalite',
            'poste', 'courriel', 'adresse', 'ville', 'pays',
            'code_postal', 'telephone', 'telecopieur', 'accompagnateur',
            'accompagnateur_genre', 'accompagnateur_nom',
            'accompagnateur_prenom'
        )
        widgets = dict(
            (f, forms.TextInput(attrs={'size': 40}))
            for f in ('nom', 'prenom', 'nationalite', 'poste', 'courriel',
                      'ville', 'pays', 'accompagnateur_nom',
                      'accompagnateur_prenom')
        )

    def require_fields(self):
        for name, field in self.fields.iteritems():
            if name.startswith('accompagnateur_'):
                # Afficher comme un champ obligatoire, mais ne pas valider
                # automatiquement.
                field.widget.is_required = True
            elif name not in (
                'code_postal', 'telecopieur', 'accompagnateur'
            ):
                field.required = True
                field.widget.is_required = True

    def clean_accompagnateur_genre(self):
        return self._clean_accompagnateur_field('genre')

    def clean_accompagnateur_nom(self):
        return self._clean_accompagnateur_field('nom')

    def clean_accompagnateur_prenom(self):
        return self._clean_accompagnateur_field('prenom')

    def _clean_accompagnateur_field(self, field):
        value = self.cleaned_data.get('accompagnateur_' + field)
        if self.cleaned_data.get('accompagnateur') and not value:
            raise forms.ValidationError('Ce champ est obligatoire.')
        return value


class ProgrammationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProgrammationForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            field = self.fields[key]
            infos_montant = infos_montant_par_nom_champ(key)
            if infos_montant:
                field.help_text = infos_montant.affiche

    class Meta:
        model = Inscription
        fields = (
            'programmation_soiree_unesp', 'programmation_soiree_unesp_invite',
            'programmation_soiree_interconsulaire',
            'programmation_soiree_interconsulaire_invite',
            'programmation_gala',
            'programmation_gala_invite'
        )

    def clean_programmation_soiree_unesp_invite(self):
        return self._clean_invite_field('programmation_soiree_unesp')

    def clean_programmation_soiree_interconsulaire_invite(self):
        return self._clean_invite_field('programmation_soiree_interconsulaire')

    def clean_programmation_gala_invite(self):
        return self._clean_invite_field(
            'programmation_gala'
        )

    def _clean_invite_field(self, field):
        return self.cleaned_data.get(field) and \
                self.cleaned_data.get(field + '_invite')

    def require_fields(self):
        pass


def transport_widgets():
    widgets = dict(
        (f, forms.DateInput(attrs={'class': 'date'}))
            for f in ('arrivee_date', 'depart_date')
    )
    widgets.update({
        #'type_chambre_hotel': RadioSelect(),
        'date_naissance': forms.DateInput(attrs={'size': 10})
    })
    return widgets


def get_date_hotel_choices(depart_ou_arrivee):
    choices = [(u"", u"-----")]
    nombre_jours = (
        Inscription.DATE_HOTEL_MAX - Inscription.DATE_HOTEL_MIN
    ).days + 1
    premier_jour = Inscription.DATE_HOTEL_MIN \
            if depart_ou_arrivee == 'arrivee' \
            else Inscription.DATE_HOTEL_MIN + datetime.timedelta(days=1)
    for numero_jour in xrange(nombre_jours):
        date = premier_jour + datetime.timedelta(days=numero_jour)
        date_str = date.strftime('%d %B %Y')
        choices.append((date.isoformat(), date_str))
    return choices


#def get_type_chambre_choices():
#    model_choices = Inscription.TYPE_CHAMBRE_CHOICES
#    choices = (
#        (
#            model_choices[0][0],
#            mark_safe(
#                model_choices[0][1] + ' ' +
#                str(infos_montant_par_code('hebergement_simple').montant) +
#                ' &euro;'
#            )
#        ),
#        (
#            model_choices[1][0],
#            mark_safe(
#                model_choices[1][1] + ' ' +
#                str(infos_montant_par_code('hebergement_double').montant) +
#                ' &euro;'
#            )
#        ),
#    )
#    return choices
#

class TransportHebergementForm(forms.ModelForm):
    prise_en_charge_hebergement = forms.NullBooleanField(
        label='', required=False,
        widget=forms.RadioSelect(choices=(
            ('True', "Je demande la prise en charge de mon hébergement."),
            ('False', "Je m'occupe moi-même de mon hébergement."),
        ))
    )
    prise_en_charge_transport = forms.NullBooleanField(
        label='', required=False,
        widget=forms.RadioSelect(choices=(
            ('True', "Je demande la prise en charge de mon transport."),
            ('False', "Je m'occupe moi-même de mon transport."),
        ))
    )
    depart_de = forms.ChoiceField(
        choices=Inscription.DEPART_DE_CHOICES, required=False,
        widget=forms.RadioSelect
    )
    date_arrivee_hotel = forms.ChoiceField(label=u"Date d'arrivée à l'hôtel",
        choices=get_date_hotel_choices('arrivee'), required=True)
    date_depart_hotel = forms.ChoiceField(label=u"Date de départ de l'hôtel",
        choices=get_date_hotel_choices('depart'), required=True)

    date_naissance = forms.DateField(required=True)

    class Meta:
        model = Inscription
        fields = (
            'prise_en_charge_hebergement', 'prise_en_charge_transport',
            'date_arrivee_hotel',
            'date_depart_hotel', 'date_naissance', 'arrivee_date',
            'arrivee_heure', 'arrivee_compagnie', 'arrivee_vol',
            'depart_de', 'depart_date', 'depart_heure', 'depart_compagnie',
            'depart_vol'
        )
        widgets = transport_widgets()

    def __init__(self, *args, **kwargs):
        super(TransportHebergementForm, self).__init__(*args, **kwargs)
        #self.fields['type_chambre_hotel'].choices = get_type_chambre_choices()

    def require_fields(self):
        #self.fields['type_chambre_hotel'].required = False
        self.fields['date_arrivee_hotel'].required = False
        self.fields['date_depart_hotel'].required = False
        self.fields['date_naissance'].required = False
        inscription = self.instance
        if inscription.prise_en_charge_hebergement_possible():
            field = self.fields['prise_en_charge_hebergement']
            field.required = True
            field.widget.required = True
        if inscription.prise_en_charge_transport_possible():
            field = self.fields['prise_en_charge_transport']
            field.required = True
            field.widget.required = True

    def clean_prise_en_charge_hebergement(self):
        return self._clean_prise_en_charge_field('hebergement')

    def clean_prise_en_charge_transport(self):
        return self._clean_prise_en_charge_field('transport')

    def _clean_prise_en_charge_field(self, field):
        required = self.fields['prise_en_charge_' + field].required
        value = self.cleaned_data.get('prise_en_charge_' + field)
        if required and value is None:
            raise forms.ValidationError('Ce champ est obligatoire')
        return value

    def clean_date_depart_hotel(self):
        return self._clean_date_hotel('depart')

    def clean_date_arrivee_hotel(self):
        return self._clean_date_hotel('arrivee')

    def _clean_date_hotel(self, depart_ou_arrivee):
        value = self.cleaned_data.get('date_' + depart_ou_arrivee + '_hotel')
        value = None if value == u"" else value
        return value

    def clean_date_naissance(self):
        required = self.cleaned_data.get('prise_en_charge_transport', False)
        value = self.cleaned_data.get('date_naissance')
        if required and not value:
            raise forms.ValidationError('Ce champ est obligatoire')
        return value


# sandbox:  merchant berang_1344607404_biz@auf.org / 344607384
#           buyer berang_1344628599_per@auf.org 344628567


class PaiementForm(forms.ModelForm):
    paiement = forms.ChoiceField(
        label='Modalités de paiement', choices=Inscription.PAIEMENT_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Inscription
        fields = ('paiement',)

    def require_fields(self):
        self.fields['paiement'].required = True

PAYPAL_DATE_FORMATS = ("%H:%M:%S %b. %d, %Y PST",
                      "%H:%M:%S %b. %d, %Y PDT",
                      "%H:%M:%S %b %d, %Y PST",
                      "%H:%M:%S %b %d, %Y PDT",)


class PaypalNotificationForm(forms.Form):
    mc_gross = forms.FloatField(required=False)
    mc_currency = forms.CharField(required=False)
    invoice = forms.CharField(required=False)
    payment_date = forms.DateTimeField(input_formats=PAYPAL_DATE_FORMATS)
    payment_status = forms.CharField(required=False)
    pending_reason = forms.CharField(required=False)
    txn_id = forms.CharField(required=False)
