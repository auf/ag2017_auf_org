from django.forms import ModelForm,  modelformset_factory, RadioSelect
from django.forms.fields import ChoiceField
from django.forms.models import BaseModelFormSet

from ag.gestion.models import Participant
from .models import Election


class CandidatureForm(ModelForm):
    class Meta:
        model = Participant
        fields = ('candidat_a', 'suppleant_de', 'candidat_libre',
                  'candidat_elimine')
        widgets = {'candidat_a': RadioSelect}

    candidat_a = ChoiceField(widget=RadioSelect)

    def __init__(self, *args, **kwargs):
        elections = kwargs.pop('elections')
        super(CandidatureForm, self).__init__(*args, **kwargs)
        self.fields['candidat_a'].empty_label = u"Aucune"
        self.fields['candidat_a'].choices = [(u"", u"Aucune")] + [
            (unicode(e.id), e.code) for e in elections]


class BaseCandidatureFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseCandidatureFormset, self).__init__(*args, **kwargs)
        self.elections = list(Election.objects.all())

    def _construct_form(self, i, **kwargs):
        kwargs['elections'] = self.elections
        return super(BaseCandidatureFormset, self)._construct_form(i, **kwargs)

CandidatureFormset = modelformset_factory(
    Participant, CandidatureForm, extra=0, can_delete=False, can_order=False,
    formset=BaseCandidatureFormset)
