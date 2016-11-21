# -*- encoding: utf-8 -*-
import collections
import ag.inscription.models as models_inscription
import ag.gestion.models as models_gestion


SuiviDossier = collections.namedtuple(
    'SuiviDossier', ('inscription_recue', 'inscription_validee',
                     'participation_confirmee', 'plan_de_vol_complete'))


class InscriptionFermee(models_inscription.Inscription):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(InscriptionFermee, self).__init__(*args, **kwargs)

    def get_participant(self):
        if not hasattr(self, '_participant'):
            try:
                self._participant = models_gestion.Participant.objects \
                    .sql_extra_fields('total_facture', 'total_deja_paye_sql')\
                    .get(inscription__id=self.id)
                print('total_facture=' + str(self._participant.total_facture))
            except models_gestion.Participant.DoesNotExist:
                return None
        return self._participant

    def get_participant_or_self(self):
        return self.get_participant() or self

    def get_adresse(self):
        participant = self.get_participant()
        if participant:
            return participant.get_adresse()
        else:
            return super(InscriptionFermee, self).get_adresse()

    def set_adresse(self, adresse):
        """Fixe l'adresse du participant si l'inscription a été validée, sinon
        fixe l'adresse de l'inscription

        :param adresse: Adresse
        """
        dest = self.get_participant_or_self()
        dest.adresse = adresse.adresse
        dest.code_postal = adresse.code_postal
        dest.ville = adresse.ville
        dest.pays = adresse.pays

    def is_participation_confirmee(self):
        participant = self.get_participant()
        return bool(participant and participant.facturation_validee)

    def is_plan_de_vol_complete(self):
        participant = self.get_participant()
        return bool(
            participant and
            participant.statut_dossier_transport == models_gestion.COMPLETE)

    def get_suivi_dossier(self):
        participant = self.get_participant()
        return SuiviDossier(
            inscription_recue=self.fermee,
            inscription_validee=participant is not None,
            participation_confirmee=self.is_participation_confirmee(),
            plan_de_vol_complete=self.is_plan_de_vol_complete())

    def a_televerse_passeport(self):
        participant = self.get_participant()
        if participant:
            return participant.a_televerse_passeport()
        else:
            return False

    @property
    def total_facture(self):
        if self.get_participant():
            return self.get_participant().total_facture
        else:
            return super(InscriptionFermee, self).total_facture

    @property
    def total_deja_paye(self):
        if self.get_participant():
            return self.get_participant().total_deja_paye
        else:
            return super(InscriptionFermee, self).total_deja_paye

    def get_prise_en_charge_hebergement(self):
        if self.get_participant():
            return self.get_participant().prise_en_charge_sejour
        else:
            return self.prise_en_charge_hebergement
