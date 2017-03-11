# -*- encoding: utf-8 -*-
from django.forms import Form,  formset_factory, RadioSelect, ChoiceField, \
    BooleanField, BaseFormSet

from ag.elections.models import Candidat
from ag.elections.models import Candidats, get_candidats_possibles
from .models import Election


def suppleant_de_choices(participant, candidats_ca):
    return [(u"", u"Personne")] + [
        (unicode(candidat.id), candidat.get_nom_complet())
        for candidat in candidats_ca
        if candidat != participant]


class CandidatureForm(Form):
    election = ChoiceField(choices=(), widget=RadioSelect,
                           required=False)
    suppleant_de_id = ChoiceField(choices=(), required=False)
    libre = BooleanField(required=False)
    elimine = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.elections = elections = kwargs.pop('elections')
        candidat = self.candidat = kwargs.pop('candidat')
        # type: Candidat
        candidats = self.candidats = kwargs.pop('candidats')
        # type: Candidats
        self.suppleant = candidats.get_suppleant(candidat)
        super(CandidatureForm, self).__init__(*args, **kwargs)
        self.fields['election'].choices = \
            [(u"", u"Aucune")] + \
            [(unicode(e.id), e.code) for e in elections] + \
            [(u"S", u"Suppléant")]
        self.fields['suppleant_de_id'].choices = \
            candidats.get_suppleant_de_choices(self.candidat)
        self.candidatures_possibles = [
            unicode(e.id) for e in elections
            if e.code in self.candidat.candidatures_possibles]
        if candidat.peut_etre_suppleant:
            self.candidatures_possibles += [SUPPLEANT]

    def get_updated_candidat(self):
        d = self.cleaned_data
        election = d['election']
        if election == SUPPLEANT and d['suppleant_de_id']:
            suppleant_de_id = int(d['suppleant_de_id'])
        else:
            suppleant_de_id = None
        if election == SUPPLEANT or not election:
            election_id = None
        else:
            election_id = int(election)

        # noinspection PyProtectedMember
        return self.candidat._replace(**{
            'suppleant_de_id': suppleant_de_id,
            'election': election_id,
            'libre': d['libre'],
            'elimine': d['elimine']
        })


SUPPLEANT = u"S"


def candidat_to_form_data(candidat):
    election = SUPPLEANT if candidat.suppleant_de_id else candidat.election
    return {
        'election': election or u"",
        'suppleant_de_id': candidat.suppleant_de_id,
        'libre': candidat.libre or False,
        'elimine': candidat.elimine or False,
    }


class BaseCandidatureFormset(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.candidats = get_candidats_possibles()
        self.grouped_by_region = self.candidats.grouped_by_region()
        kwargs['initial'] = [candidat_to_form_data(c) for c in
                             self.grouped_by_region]
        super(BaseCandidatureFormset, self).__init__(*args, **kwargs)
        self.elections = list(Election.objects.all())

    def _construct_form(self, i, **kwargs):
        kwargs['elections'] = self.elections
        kwargs['candidat'] = self.grouped_by_region[i]
        kwargs['candidats'] = self.candidats
        return super(BaseCandidatureFormset, self)._construct_form(i, **kwargs)

    def get_updated_candidats(self):
        return Candidats([form.get_updated_candidat() for form in self])


CandidatureFormset = formset_factory(
    CandidatureForm, extra=0, can_delete=False, can_order=False,
    formset=BaseCandidatureFormset)

