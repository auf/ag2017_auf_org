# -*- encoding: utf-8 -*-
import django.test
from ag.core.test_utils import InscriptionFactory, ParticipantFactory
from ag.dossier_inscription.models import (
    Adresse,
    InscriptionFermee, )
from ag.gestion.models import Participant


class InscriptionFermeeTests(django.test.TestCase):
    def test_get_adresse_self(self):
        """Si l'inscription n'a pas été validée, l'adresse retournée est
        l'adresse de l'objet Inscription.
        """
        adresse = Adresse(adresse="adr", code_postal="12345", ville="laville")
        i = InscriptionFermee(**adresse.__dict__)
        assert i.get_adresse() == adresse

    def test_get_adresse_participant(self):
        """Si l'inscription a été validée, un objet participant a été créé
        pour elle, et c'est l'adresse contenue dans Participant que get_adresse
        doit retourner.
        """
        adresse_part = Adresse(adresse="adrpart", code_postal="98765",
                               ville="lavillepart")
        i = InscriptionFactory()
        ParticipantFactory(inscription=i, **adresse_part.__dict__)
        i = InscriptionFermee.objects.get(id=i.id)
        assert i.get_adresse() == adresse_part
