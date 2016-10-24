# -*- encoding: utf-8 -*-
from django import forms
import ag.inscription.models
from ag.gestion import models as gestion_models


class AdresseForm(forms.Form):
    required_css_class = 'required'

    adresse = forms.CharField(widget=forms.Textarea, required=True)
    ville = forms.CharField(max_length=100, required=True)
    code_postal = forms.CharField(max_length=100, required=True)
    pays = forms.CharField(max_length=100, required=True)


class InviteForm(forms.Form):
    nom = forms.CharField(max_length=100, required=True)
    prenom = forms.CharField(label=u"prénom", max_length=100, required=True)
    courriel = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'invite-widget'

InvitesFormSet = forms.formset_factory(InviteForm, extra=2)


class FiltreReseautageForm(forms.Form):
    region = forms.ChoiceField(label=u"Région", required=False)
    pays = forms.ChoiceField(required=False)

    def __init__(self, regions, pays, *args, **kwargs):
        super(FiltreReseautageForm, self).__init__(*args, **kwargs)
        self.fields['region'].choices = regions
        self.fields['pays'].choices = pays


class PlanVolForm(forms.ModelForm):
    class Meta:
        model = ag.inscription.models.Inscription
        fields = ('depart_date', 'depart_heure', 'depart_vol',
                  'arrivee_date', 'arrivee_heure', 'arrivee_vol')


class AjoutPasseportForm(forms.ModelForm):
    class Meta:
        model = gestion_models.Fichier
        exclude = ('participant', 'cree_le', 'cree_par', 'efface_par',
                   'efface_le', 'type_fichier')
        labels = {
            'fichier': u"Sélectionnez le fichier image de votre passeport"
        }

    def save(self, commit=True):
        fichier = super(AjoutPasseportForm, self).save(commit)
        fichier.type_fichier = 1
        fichier.save()
        return fichier
