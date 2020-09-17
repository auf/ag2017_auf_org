# -*- encoding: utf-8 -*-
from django.forms import (Form, EmailField, ModelMultipleChoiceField,
                          CheckboxSelectMultiple, ModelChoiceField,
                          RadioSelect)

from ag.gestion.models import ActiviteScientifique


class LoginForm(Form):
    email = EmailField(label="Inscrivez votre courriel pour sélectionner l'atelier auquel vous souhaitez participer")


class PickForm(Form):
    activites = ModelChoiceField(
        queryset=ActiviteScientifique.objects.all(),
        widget=RadioSelect,
        empty_label=None, label="")
    # activites = ModelMultipleChoiceField(
    #     queryset=ActiviteScientifique.objects.all(),
    #     widget=CheckboxSelectMultiple)
