# -*- encoding: utf-8 -*-
from django.forms import Form, formset_factory, RadioSelect, ChoiceField, \
    BooleanField, BaseFormSet, IntegerField, HiddenInput, DateTimeField
from django.forms.formsets import INITIAL_FORM_COUNT

from ag.elections.models import (
    Candidat,
    peut_etre_suppleant,
    Candidats,
)
from ag.gestion import consts


class CandidatureForm(Form):
    participant_id = IntegerField(required=True, widget=HiddenInput)
    election = ChoiceField(choices=(), widget=RadioSelect,
                           required=False)
    suppleant_de_id = ChoiceField(choices=(), required=False)
    libre = BooleanField(required=False)
    statut = ChoiceField(choices=consts.STATUTS_CANDIDATS, required=False)
    last_modified = DateTimeField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        self.elections = elections = kwargs.pop('elections')
        candidat = self.candidat = kwargs.pop('candidat')
        # type: Candidat
        candidats = self.candidats = kwargs.pop('candidats')
        # type: Candidats
        self.suppleant = candidats.get_suppleant(candidat)
        kwargs['initial'] = candidat_to_form_data(candidat)
        super(CandidatureForm, self).__init__(*args, **kwargs)
        self.fields['election'].choices = \
            [("", "Aucune")] + \
            [(e.code, e.code) for e in elections] + \
            [("S", "Suppléant")]
        self.fields['suppleant_de_id'].choices = \
            candidats.get_suppleant_de_choices(self.candidat)
        candidatures_possibles = self.candidat.candidatures_possibles
        if peut_etre_suppleant(candidat):
            candidatures_possibles |= {SUPPLEANT}
        self.candidatures_possibles = candidatures_possibles

    def get_updated_candidat(self):
        d = self.cleaned_data
        code_election = d['election']
        if code_election == SUPPLEANT and d['suppleant_de_id']:
            suppleant_de_id = int(d['suppleant_de_id'])
        else:
            suppleant_de_id = None
        if code_election == SUPPLEANT or not code_election:
            code_election = None
        statut = d.get('statut', consts.DANS_LA_COURSE) or consts.DANS_LA_COURSE

        # noinspection PyProtectedMember
        return self.candidat._replace(**{
            'suppleant_de_id': suppleant_de_id,
            'code_election': code_election,
            'libre': d['libre'],
            'last_modified': d['last_modified'],
            'statut': statut,
        })


SUPPLEANT = "S"


def candidat_to_form_data(candidat):
    election = SUPPLEANT if candidat.suppleant_de_id else candidat.code_election
    return {
        'participant_id': candidat.participant_id,
        'election': election or "",
        'suppleant_de_id': candidat.suppleant_de_id,
        'libre': candidat.libre or False,
        'statut': candidat.statut,
        'last_modified': candidat.last_modified,
    }


class BaseCandidatureFormset(BaseFormSet):
    def __init__(self, *args, **kwargs):
        candidats = kwargs.pop('candidats')
        self.elections = kwargs.pop('elections')
        self.candidats = candidats
        self.grouped_by_region = self.candidats.grouped_by_region()
        super(BaseCandidatureFormset, self).__init__(*args, **kwargs)

    def initial_form_count(self):
        """Returns the number of forms that are required in this FormSet."""
        if self.is_bound:
            return self.management_form.cleaned_data[INITIAL_FORM_COUNT]
        else:
            # Use the length of the initial data if it's there, 0 otherwise.
            initial_forms = len(self.candidats)
        return initial_forms

    def _construct_form(self, i, **kwargs):
        kwargs['elections'] = self.elections
        kwargs['candidats'] = self.candidats
        if self.is_bound:
            participant_id_field = "{}-{}".format(self.add_prefix(i),
                                                   'participant_id')
            participant_id = int(self.data[participant_id_field])
            candidat = self.candidats.get_candidat(participant_id)
        else:
            candidat = self.grouped_by_region[i]
        kwargs['candidat'] = candidat
        return super(BaseCandidatureFormset, self)._construct_form(i, **kwargs)

    def get_form_by_participant_id(self, participant_id):
        for form in self:
            if form.candidat.participant_id == participant_id:
                return form

    def get_updated_candidats(self):
        return Candidats([form.get_updated_candidat() for form in self])


CandidatureFormset = formset_factory(
    CandidatureForm, extra=0, can_delete=False, can_order=False,
    formset=BaseCandidatureFormset)

