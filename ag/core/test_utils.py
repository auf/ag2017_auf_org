# -*- encoding: utf-8 -*-

import factory
import ag.reference.models as ref_models
import ag.inscription.models as inscription_models
import ag.gestion.models as gestion_models


def find_input_by_id(tree, html_id):
        return tree.find("//input[@id='{0}']".format(html_id))


def find_input_by_name(tree, html_name):
        return tree.find("//input[@name='{0}']".format(html_name))


def find_checked_input_by_name(tree, html_name):
    return tree.find("//input[@name='{0}'][@checked='checked']".format(html_name))


# noinspection PyUnresolvedReferences
class PaysFactory(factory.DjangoModelFactory):
    class Meta:
        model = ref_models.Pays
    code = factory.Sequence(lambda n: '{0}'.format(int(n) % 99))
    nom = factory.LazyAttribute(lambda a: 'Pays ' + a.code)
    sud = False


# noinspection PyUnresolvedReferences
class RegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = ref_models.Region
    code = factory.Sequence(lambda n: 'R{0}'.format(n))
    nom = factory.LazyAttribute(lambda a: 'Region ' + a.code)


# noinspection PyUnresolvedReferences
class EtablissementFactory(factory.DjangoModelFactory):
    class Meta:
        model = ref_models.Etablissement
    nom = factory.Sequence(lambda n: u"Etablissement {0}".format(n))
    pays = factory.SubFactory(PaysFactory)
    region = factory.SubFactory(RegionFactory)
    qualite = "ESR"


# noinspection PyUnresolvedReferences
class StatutFactory(factory.DjangoModelFactory):
    class Meta:
        model = gestion_models.StatutParticipant
    ordre = factory.Sequence(lambda n: n)
    code = factory.Sequence(lambda n: 'SP{0}'.format(n))
    libelle = factory.LazyAttribute(lambda a: 'StatutParticipant ' + a.code)


# noinspection PyUnresolvedReferences
class InvitationFactory(factory.DjangoModelFactory):
    class Meta:
        model = inscription_models.Invitation
    etablissement = factory.SubFactory(EtablissementFactory)


# noinspection PyUnresolvedReferences
class InscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = inscription_models.Inscription

    invitation = factory.SubFactory(InvitationFactory)


# noinspection PyUnresolvedReferences
class ParticipantFactory(factory.DjangoModelFactory):
    class Meta:
        model = gestion_models.Participant

    statut = factory.SubFactory(StatutFactory)
