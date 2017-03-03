from django.forms import ModelForm,  modelformset_factory

from ag.gestion.models import Participant


class CandidatureForm(ModelForm):
    class Meta:
        model = Participant
        fields = ('candidat_a', 'suppleant_de', 'candidat_libre',
                  'candidat_elimine')


CandidatureFormset = modelformset_factory(
    Participant, CandidatureForm, extra=0, can_delete=False, can_order=False)
