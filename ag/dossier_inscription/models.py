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

    def get_participant(self):
        try:
            return self.participant
        except models_gestion.Participant.DoesNotExist:
            return None

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
        return participant.a_televerse_passeport()
