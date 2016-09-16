# -*- encoding: utf-8 -*-
import collections
import ag.inscription.models as models_inscription
import ag.gestion.models as models_gestion


Adresse = collections.namedtuple('Adresse', ('adresse', 'ville', 'code_postal'))


class InscriptionFermee(models_inscription.Inscription):
    class Meta:
        proxy = True

    def get_participant_or_self(self):
        try:
            return self.participant
        except models_gestion.Participant.DoesNotExist:
            return self

    def get_adresse(self):
        source = self.get_participant_or_self()
        return Adresse(source.adresse, source.ville, source.code_postal)

    def set_adresse(self, adresse):
        """Fixe l'adresse du participant si l'inscription a été validée, sinon
        fixe l'adresse de l'inscription

        :param adresse: Adresse
        """
        dest = self.get_participant_or_self()
        dest.adresse = adresse.adresse
        dest.code_postal = adresse.code_postal
        dest.ville = adresse.ville


