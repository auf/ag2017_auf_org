# -*- encoding: utf-8 -*-
from django.forms import Form,  formset_factory, RadioSelect, ChoiceField, \
    BooleanField, BaseFormSet

from ag.elections.models import Candidats, get_candidats_possibles
from ag.gestion.models import Participant
from .models import Election


def suppleant_de_choices(participant, candidats_ca):
    return [(u"", u"Personne")] + [
        (unicode(candidat.id), candidat.get_nom_complet())
        for candidat in candidats_ca
        if candidat != participant]


class CandidatureForm(Form):
    class Meta:
        model = Participant
        fields = ('suppleant_de', 'candidat_libre',
                  'candidat_elimine', 'candidat_a_election')

    election = ChoiceField(choices=(), widget=RadioSelect,
                           required=False)
    suppleant_de_id = ChoiceField(choices=(), required=False)
    libre = BooleanField()
    elimine = BooleanField()

    def __init__(self, *args, **kwargs):
        self.elections = elections = kwargs.pop('elections')
        candidat = self.candidat = kwargs.pop('candidat')
        candidats = self.candidats = kwargs.pop('candidats')
        # type: Candidats
        super(CandidatureForm, self).__init__(*args, **kwargs)
        self.fields['candidat_a_election'].choices = \
            [(u"", u"Aucune")] + \
            [(unicode(e.id), e.code) for e in elections] + \
            [(u"S", u"Suppléant")]
        self.fields['suppleant_de'].choices = \
            candidats.get_suppleant_de_choices(self.candidat)
        self.candidatures_possibles = [
            unicode(e.id) for e in elections
            if e.code in self.candidat.candidatures_possibles] + \
            [self.SUPPLEANT]

SUPPLEANT = u"S"


def candidat_to_form_data(candidat):
    election = SUPPLEANT if candidat.suppleant_de_id else candidat.election
    return {
        'election': election or u"",
        'suppleant_de_id': candidat.suppleant_de_id,
        'libre': candidat.libre,
        'elimine': candidat.elimine,
    }


class BaseCandidatureFormset(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.candidats = get_candidats_possibles()
        kwargs['initial'] = [candidat_to_form_data(c) for c in
                             self.candidats.grouped_by_region()]
        super(BaseCandidatureFormset, self).__init__(*args, **kwargs)
        self.elections = list(Election.objects.all())

    def _construct_form(self, i, **kwargs):
        kwargs['elections'] = self.elections
        kwargs['candidat'] = self.candidats[i]
        return super(BaseCandidatureFormset, self)._construct_form(i, **kwargs)


CandidatureFormset = formset_factory(
    CandidatureForm, extra=0, can_delete=False, can_order=False,
    formset=BaseCandidatureFormset)

