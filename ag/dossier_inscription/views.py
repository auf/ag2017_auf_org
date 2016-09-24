# -*- encoding: utf-8 -*-
import collections
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
import ag.inscription.views as inscription_views
from ag.dossier_inscription import forms
from ag.dossier_inscription.models import InscriptionFermee, Adresse

InfoVirement = collections.namedtuple(
    'InfoVirement', ('nom_region', 'releve', 'code_banque', 'code_guichet',
                     'num_compte', 'cle_rib', 'id_international', 'iban',
                     'bic', 'domiciliation', 'titulaire'))


def dossier(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    adresse = inscription.get_adresse()
    # noinspection PyProtectedMember
    context = {
        'inscription': inscription,
        'adresse': adresse,
        'suivi': inscription.get_suivi_dossier(),
        'solde': inscription.get_total_du(),
        'form_adresse': forms.AdresseForm(initial=adresse._asdict()),
        'info_virement': INFOS_VIREMENT[inscription.get_region().code]
    }
    context.update(inscription_views.get_paypal_context(request))
    return render(request, 'dossier_inscription/dossier.html', context)


@require_POST
def set_adresse(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = InscriptionFermee.objects.get(id=inscription_id)
    form_adresse = forms.AdresseForm(request.POST)
    if form_adresse.is_valid():
        inscription.set_adresse(Adresse(**form_adresse.cleaned_data))
        inscription.save()
    return render(request, 'dossier_inscription/includes/adresse.html',
                  {'adresse': inscription.get_adresse(),
                   'form_adresse': form_adresse})


INFOS_VIREMENT = {
    "AP": InfoVirement(
        nom_region="Asie Pacifique",
        releve="RIB_AP", 
        code_banque="codebnk_AP",
        code_guichet="codguic_AP",
        num_compte="numcpt_AP",
        cle_rib="clerib_AP",
        id_international="idint_AP",
        iban="iban_AP",
        bic="bic_AP",
        domiciliation="domic_AP",
        titulaire="titulaire_AP"
    ),
    "MO": InfoVirement(
        nom_region="Moyen-Orient",
        releve="RIB_MO", 
        code_banque="codebnk_MO",
        code_guichet="codguic_MO",
        num_compte="numcpt_MO",
        cle_rib="clerib_MO",
        id_international="idint_MO",
        iban="iban_MO",
        bic="bic_MO",
        domiciliation="domic_MO",
        titulaire="titulaire_MO"
    ),
    "M": InfoVirement(
        nom_region="Maghreb",
        releve="RIB_M", 
        code_banque="codebnk_M",
        code_guichet="codguic_M",
        num_compte="numcpt_M",
        cle_rib="clerib_M",
        id_international="idint_M",
        iban="iban_M",
        bic="bic_M",
        domiciliation="domic_M",
        titulaire="titulaire_M"
    ),
    "EO": InfoVirement(
        nom_region="Europe occidentale",
        releve="RIB_EO", 
        code_banque="codebnk_EO",
        code_guichet="codguic_EO",
        num_compte="numcpt_EO",
        cle_rib="clerib_EO",
        id_international="idint_EO",
        iban="iban_EO",
        bic="bic_EO",
        domiciliation="domic_EO",
        titulaire="titulaire_EO"
    ),
    
}
