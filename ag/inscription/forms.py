# encoding: utf-8
import datetime
from django import forms
from ag.inscription.models import Inscription, CODES_CHAMPS_MONTANTS


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        exclude = ()


class AccueilForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ('identite_accompagnateur_confirmee', 'atteste_pha',
                  'conditions_acceptees')
        widgets = {
            'atteste_pha': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(AccueilForm, self).__init__(*args, **kwargs)
        assert self.instance is not None
        atteste_pha = self.fields['atteste_pha']
        if self.instance.est_pour_mandate():
            del self.fields['identite_accompagnateur_confirmee']
            # seul moyen pour supprimer choix vide
            atteste_pha.choices = atteste_pha.choices[1:]
            atteste_pha.label = u""
            atteste_pha.required = True
        else:
            del atteste_pha
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
            self.fields['identite_accompagnateur_confirmee'].label = label
        self.require_fields()

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
            'genre', 'nom', 'prenom', 'poste', 'courriel', 'adresse', 'ville',
            'pays', 'code_postal', 'telephone', 'telecopieur', 'accompagnateur',
            'accompagnateur_genre', 'accompagnateur_nom',
            'accompagnateur_prenom'
        )
        widgets = dict(
            (f, forms.TextInput(attrs={'size': 40}))
            for f in ('nom', 'prenom', 'poste', 'courriel',
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
                'telecopieur', 'accompagnateur'
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
        infos_montants = kwargs.pop('infos_montants')
        super(ProgrammationForm, self).__init__(*args, **kwargs)
        for key in self.champs_montants():
                infos_montant = infos_montants[CODES_CHAMPS_MONTANTS[key]]
                self.fields[key].help_text = infos_montant.affiche
        self.infos_montants = infos_montants

    class Meta:
        model = Inscription
        fields = (
            'programmation_soiree_9_mai', 'programmation_soiree_9_mai_invite',
            'programmation_soiree_10_mai', 'programmation_soiree_10_mai_invite',
            'programmation_gala', 'programmation_gala_invite',
            'programmation_soiree_12_mai',
            'forfait_invite_dejeuners', 'forfait_invite_transfert',
        )

    def champs_montants(self):
        return (key for key in self.fields if key in CODES_CHAMPS_MONTANTS)

    def clean_programmation_soiree_9_mai_invite(self):
        return self._clean_invite_field('programmation_soiree_9_mai')

    def clean_programmation_soiree_10_mai_invite(self):
        return self._clean_invite_field('programmation_soiree_10_mai')

    def clean_programmation_gala_invite(self):
        return self._clean_invite_field(
            'programmation_gala'
        )

    def _clean_invite_field(self, field):
        return self.cleaned_data.get(field) and \
                self.cleaned_data.get(field + '_invite')

    def require_fields(self):
        pass


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

    class Meta:
        model = Inscription
        fields = (
            'prise_en_charge_hebergement', 'prise_en_charge_transport',
        )

    def require_fields(self):
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
