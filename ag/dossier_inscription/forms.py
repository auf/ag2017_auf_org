# -*- encoding: utf-8 -*-
from django import forms


class AdresseForm(forms.Form):
    required_css_class = 'required'

    adresse = forms.CharField(widget=forms.Textarea, required=True)
    ville = forms.CharField(max_length=100, required=True)
    code_postal = forms.CharField(max_length=100, required=True)
    pays = forms.CharField(max_length=100, required=True)
