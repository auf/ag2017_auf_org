# -*- encoding: utf-8 -*-
import collections

import ag.gestion.models as models_gestion
import ag.inscription.models as models_inscription

SuiviDossier = collections.namedtuple(
    'SuiviDossier', ('inscription_recue', 'inscription_validee',
                     'participation_confirmee', 'plan_de_vol_complete'))


def infos_depart_arrivee_from_inscription(inscription):
    """

    :param inscription: models_inscription.Inscription
    :return: InfosDepartArrivee
    """
    # noinspection PyProtectedMember
    return models_gestion.InfosDepartArrivee(
        **{field: getattr(inscription, field)
           for field in models_gestion.InfosDepartArrivee._fields})


def infos_depart_arrivee_to_inscription(infos_depart_arrivee, inscription):
    # noinspection PyProtectedMember
    for field in models_gestion.InfosDepartArrivee._fields:
        setattr(inscription, field, getattr(infos_depart_arrivee, field))


def infos_depart_arrivee_to_participant(infos_depart_arrivee, participant):
    """
    
    :param infos_depart_arrivee: InfosDepartArrivee
    :param participant: models_gestion.Participant
    """

    participant.set_infos_arrivee(infos_depart_arrivee.arrivee_date,
                                  infos_depart_arrivee.arrivee_heure,
                                  infos_depart_arrivee.arrivee_vol,
                                  infos_depart_arrivee.arrivee_compagnie,
                                  infos_depart_arrivee.arrivee_a)
    participant.set_infos_depart(infos_depart_arrivee.depart_date,
                                 infos_depart_arrivee.depart_heure,
                                 infos_depart_arrivee.depart_vol,
                                 infos_depart_arrivee.depart_compagnie,
                                 infos_depart_arrivee.depart_de)


def infos_depart_arrivee_from_participant(participant):
    infos_depart = participant.get_infos_depart()
    infos_arrivee = participant.get_infos_arrivee()
    return models_gestion.infos_depart_arrivee_from_infos_vols(infos_depart,
                                                               infos_arrivee)


class InscriptionFermee(models_inscription.Inscription):
    class Meta:
        proxy = True

    def load_participant(self):
        try:
            self._participant = models_gestion.Participant.objects \
                .sql_extra_fields('total_facture', 'total_deja_paye_sql',
                                  'frais_inscription_facture',
                                  'forfaits_invites',
                                  'frais_hebergement_facture') \
                .get(inscription__id=self.id)
        except models_gestion.Participant.DoesNotExist:
            self._participant = None

    def __init__(self, *args, **kwargs):
        super(InscriptionFermee, self).__init__(*args, **kwargs)
        self.load_participant()
        if self._participant:
            self.dossier = DossierGestion(self._participant)
        else:
            self.dossier = DossierInscription(self)

    def get_participant(self):
        return self._participant

    def get_participant_or_self(self):
        return self.get_participant() or self

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


Invite = collections.namedtuple('Invite', ('genre', 'nom', 'prenom'))


def set_adresse(dest, adresse):
    dest.adresse = adresse.adresse
    dest.code_postal = adresse.code_postal
    dest.ville = adresse.ville
    dest.pays = adresse.pays


class Dossier(object):

    def __init__(self, renseignements_personnels):
        self.rp = renseignements_personnels
        # type: models_inscription.RenseignementsPersonnels

    @property
    def genre(self):
        return self.rp.get_genre_display()

    @property
    def nom(self):
        return self.rp.nom

    @property
    def prenom(self):
        return self.rp.prenom

    @property
    def poste(self):
        return self.rp.poste

    @property
    def courriel(self):
        return self.rp.courriel


class DossierInscription(Dossier):
    def __init__(self, inscription):
        super(DossierInscription, self).__init__(inscription)
        self.inscription = inscription  # type: models_inscription.Inscription
        self.itineraire_disponible = False

    def invites(self):
        if self.inscription.accompagnateur:
            return [Invite(
                genre=self.inscription.get_accompagnateur_genre_display(),
                nom=self.inscription.accompagnateur_nom,
                prenom=self.inscription.accompagnateur_prenom)]

    def get_adresse(self):
        return self.inscription.get_adresse()

    def set_adresse(self, adresse):
        self.inscription.set_adresse(adresse)
        self.inscription.save()

    @property
    def prise_en_charge_hebergement(self):
        return self.inscription.prise_en_charge_hebergement

    def get_infos_depart_arrivee(self):
        return infos_depart_arrivee_from_inscription(self.inscription)

    def set_infos_depart_arrivee(self, infos_depart_arrivee):
        infos_depart_arrivee_to_inscription(infos_depart_arrivee,
                                            self.inscription)
        self.inscription.save()


class DossierGestion(Dossier):
    def __init__(self, participant):
        super(DossierGestion, self).__init__(participant)
        self.participant = participant  # type: models_gestion.Participant

    def invites(self):
        return [Invite(genre=i.get_genre_display(), nom=i.nom, prenom=i.prenom)
                for i in self.participant.invite_set.all()]

    @property
    def itineraire_disponible(self):
        return (self.participant.statut_dossier_transport ==
                models_gestion.COMPLETE)

    def get_adresse(self):
        return self.participant.get_adresse()

    def set_adresse(self, adresse):
        self.participant.set_adresse(adresse)
        self.participant.save()

    @property
    def prise_en_charge_hebergement(self):
        return self.participant.prise_en_charge_sejour

    def get_infos_depart_arrivee(self):
        return infos_depart_arrivee_from_participant(self.participant)

    def set_infos_depart_arrivee(self, infos_depart_arrivee):
        infos_depart_arrivee_to_participant(infos_depart_arrivee,
                                            self.participant)
        self.participant.save()
