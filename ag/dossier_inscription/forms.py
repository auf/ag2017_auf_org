# -*- encoding: utf-8 -*-
from django import forms


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
