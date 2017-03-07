from django.forms import ModelForm,  modelformset_factory, RadioSelect, \
    ModelChoiceField
from django.forms.models import BaseModelFormSet

from ag.gestion import consts
from ag.gestion.models import Participant
from .models import Election


class CandidatureForm(ModelForm):
    class Meta:
        model = Participant
        fields = ('candidat_a', 'suppleant_de', 'candidat_libre',
                  'candidat_elimine')
        widgets = {'candidat_a': RadioSelect}

    def __init__(self, *args, **kwargs):
        elections = kwargs.pop('elections')
        candidats_ca = kwargs.pop('candidats_ca')
        suppleants = kwargs.pop('suppleants')
        super(CandidatureForm, self).__init__(*args, **kwargs)
        self.fields['candidat_a'].empty_label = u"Aucune"
        self.fields['candidat_a'].choices = [(u"", u"Aucune")] + [
            (unicode(e.id), e.code) for e in elections]
        if not self.instance.candidat_avec_suppleant_possible or\
                self.instance in suppleants:
            suppleant_choices = []
        else:
            suppleant_choices = [(u"", u"Personne")] + [
                (unicode(participant.id), participant.get_nom_complet())
                for participant in candidats_ca if participant != self.instance]
        self.fields['suppleant_de'].choices = suppleant_choices
        self.candidatures_possibles = [
            unicode(e.id) for e in elections
            if e.code in self.instance.candidatures_possibles()]


class BaseCandidatureFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseCandidatureFormset, self).__init__(*args, **kwargs)
        self.elections = list(Election.objects.all())
        self.candidats_ca = list(Participant.objects.filter(
            candidat_a__code=consts.ELEC_CA))
        self.suppleants = list(Participant.objects.filter(
            candidat_a__code=consts.ELEC_CA,
            id__in=Participant.objects.values_list('suppleant_de', flat=True)))

    def _construct_form(self, i, **kwargs):
        kwargs['elections'] = self.elections
        kwargs['candidats_ca'] = self.candidats_ca
        kwargs['suppleants'] = self.suppleants
        return super(BaseCandidatureFormset, self)._construct_form(i, **kwargs)

CandidatureFormset = modelformset_factory(
    Participant, CandidatureForm, extra=0, can_delete=False, can_order=False,
    formset=BaseCandidatureFormset)
