# -*- encoding: utf-8 -*-
import datetime
import factory
import ag.reference.models as ref_models
import ag.inscription.models as inscription_models
import ag.gestion.models as gestion_models
from ag.gestion import consts


def find_input_by_id(tree, html_id):
        return tree.find("//input[@id='{0}']".format(html_id))


def find_input_by_name(tree, html_name):
        return tree.find("//input[@name='{0}']".format(html_name))


def find_checked_input_by_name(tree, html_name):
    return tree.find("//input[@name='{0}'][@checked='checked']".format(html_name))


def create_table_ref_factory(table_reference_class, abbr, extra_fields=None):
    class_name = table_reference_class.__name__
    meta_class = type('Meta', (), {
        'model': table_reference_class, })
    class_dict = {'Meta': meta_class,
                  'code': factory.Sequence(lambda n: u"{0}{1}".format(abbr, n)),
                  'libelle': factory.LazyAttribute(
                      lambda a: u"{0}{1}".format(class_name, a.code))}
    if extra_fields:
        class_dict.update(extra_fields)
    if 'ordre' in table_reference_class._meta.get_all_field_names():
        class_dict['ordre'] = factory.Sequence(lambda n: n)
    return type(class_name + 'Factory',
                (factory.DjangoModelFactory, ), class_dict)


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
    qualite = consts.CODE_ETAB_ENSEIGNEMENT


class ImplantationFactory(factory.DjangoModelFactory):
    class Meta:
        model = ref_models.Implantation
    nom = factory.Sequence(lambda n: u"Impl{0}".format(n))
    nom_court = factory.Sequence(lambda n: u"Impl{0}".format(n))
    region = factory.SubFactory(RegionFactory)


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


class PaiementFactory(factory.DjangoModelFactory):
    class Meta:
        model = gestion_models.Paiement
    date = datetime.date(2016, 10, 10)
    ref = factory.Sequence(lambda n: u"ref{0}".format(n))
    implantation = factory.SubFactory(ImplantationFactory)


TypeInstitutionFactory = create_table_ref_factory(
    gestion_models.TypeInstitution, u"TI")

CategorieFonctionFactory = create_table_ref_factory(
    gestion_models.CategorieFonction, u"CF")

FonctionFactory = create_table_ref_factory(
    gestion_models.Fonction, u"Fn",
    {'categorie': factory.SubFactory(CategorieFonctionFactory)})


class InstitutionFactory(factory.DjangoModelFactory):
    class Meta:
        model = gestion_models.Institution
    nom = factory.Sequence(lambda n: u"Inst{0}".format(n))
    pays = factory.SubFactory(PaysFactory)
    region = factory.SubFactory(RegionFactory)
