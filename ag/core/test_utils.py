# -*- encoding: utf-8 -*-

import factory
import ag.reference.models as ref_models


def find_input_by_id(tree, html_id):
        return tree.find("//input[@id='{0}']".format(html_id))


def find_input_by_name(tree, html_name):
        return tree.find("//input[@name='{0}']".format(html_name))


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
