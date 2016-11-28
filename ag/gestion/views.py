# -*- encoding: utf-8 -*-
import csv
import json
import os
import urllib
from datetime import datetime

from auf.django.permissions import require_permission
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from sendfile import sendfile
from django.conf import settings

from ag.gestion import donnees_etats
from ag.gestion import pdf
from ag.gestion import consts
from ag.gestion import forms
from ag.gestion.models import *
from ag.gestion.pdf import facture_response
from ag.reference.models import Etablissement


def liste_etablissements_json(request):
    if request.method == 'GET':
        etablissements = Etablissement.objects.select_related('pays') \
            .filter(membre=True).values('id', 'nom', 'pays__nom')
        data = json.dumps(list(etablissements))
        return HttpResponse(data, content_type="application/json")


def critere_prise_en_charge_bool(critere):
    if critere == forms.PEC_ACCEPTEE:
        return True
    elif critere == forms.PEC_REFUSEE:
        return False
    else:
        return None


def participants_view(request):
    require_permission(request.user, consts.PERM_LECTURE)
    if request.method == 'GET':
        form = forms.RechercheParticipantForm(request.GET.copy())
        if form.is_valid():
            nom = form.cleaned_data['nom']
            etablissement = form.cleaned_data['etablissement']
            suivi = form.cleaned_data['suivi']
            instance_auf = form.cleaned_data['instance_auf']
            type_institution = form.cleaned_data['type_institution']
            prise_en_charge_transport = \
                form.cleaned_data['prise_en_charge_transport']
            prise_en_charge_sejour = \
                form.cleaned_data['prise_en_charge_sejour']
            pays = form.cleaned_data['pays']
            region = form.cleaned_data['region']
            fonction = form.cleaned_data['fonction']
            probleme = form.cleaned_data['probleme']
            hotel = form.cleaned_data['hotel']
            desactive = form.cleaned_data['desactive']

            participants = Participant.objects.filter(desactive=desactive) \
                .order_by('nom', 'prenom')\
                .sql_extra_fields('delinquant')\
                .select_related('region', 'etablissement',
                                'etablissement__region', 'etablissement__pays',
                                'fonction', 'inscription')
            if nom:
                participants = participants.filter(
                    Q(nom__icontains=nom) | Q(prenom__icontains=nom)
                )
            if etablissement:
                participants = participants.filter(
                    etablissement=etablissement
                )
            else:
                form.data['etablissement_nom'] = ''
            if suivi:
                participants = participants.filter(suivi=suivi)
            if instance_auf:
                participants = participants.filter(instance_auf=instance_auf)
            if type_institution:
                participants = participants.filter(
                    fonction__type_institution=type_institution
                )
            if prise_en_charge_transport:
                participants = participants.filter(
                    prise_en_charge_transport=(
                        critere_prise_en_charge_bool(prise_en_charge_transport)
                    ))
            if prise_en_charge_sejour:
                participants = participants.filter(prise_en_charge_sejour=(
                    critere_prise_en_charge_bool(prise_en_charge_sejour)
                ))
            if pays:
                participants = participants.filter(
                    pays__icontains=pays
                )
            if region:
                participants = participants.filter(
                    Q(
                        etablissement__isnull=False,
                        etablissement__region=region
                    ) |
                    Q(region=region)
                )
            if fonction:
                participants = participants.filter(fonction=fonction)
            if hotel:
                participants = participants.filter(hotel=hotel)
            if probleme:
                if probleme == 'solde_a_payer':
                    participants = participants.sql_filter('%s > 0', 'solde')
                elif probleme == 'paiement_en_trop':
                    participants = participants.sql_filter('%s < 0', 'solde')
                else:
                    participants = participants.sql_filter('%s', probleme)
        else:
            participants = None
        liste_pays = Participant.objects.distinct().order_by('pays')\
                                .values_list('pays', flat=True)
        return render(request, 'gestion/participants.html', {
            'participants': participants, 'form': form,
            'liste_pays': liste_pays
        })


def modifier_renseignements_personnels(request, id_participant=None,
                                       cancel_to_url=''):
    participant = Participant.objects.get(id=id_participant) if id_participant \
        else None
    require_permission(request.user, 
                       consts.PERM_MODIF_RENSEIGNEMENTS_PERSONNELS,
                       obj=participant)
    if request.method == 'GET':
        form = forms.RenseignementsPersonnelsForm(instance=participant,
                                                  initial=request.GET)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect(cancel_to_url)
        post_data = request.POST.copy()  # pour pouvoir faire del
        # ce champ ne sert que pour le autocomplete, seul l'ID nous intéresse
        del post_data['etablissement_nom']
        form = forms.RenseignementsPersonnelsForm(post_data, 
                                                  instance=participant)
        if form.is_valid():
            send_signal = participant is None
            participant = form.save()
            if send_signal:
                nouveau_participant.send_robust(participant)
            if 'enregistrer_et_nouveau' in request.POST:
                return redirect(reverse('ajout_participant'))
            else:
                return redirect(reverse('fiche_participant',
                                        args=[participant.id]))
    fonctions = Fonction.objects.select_related('type_institution').all()
    institutions = Institution.objects\
        .select_related('type_institution')\
        .all()
    fonctions_json = json.dumps(
        {f.id: {'etablissement': f.repr_etablissement,
                'instance_seulement': f.repr_instance_seulement,
                'type_institution_id': f.type_institution_id}
         for f in fonctions}).replace('"', '\\"')
    institutions_json = json.dumps(
        {i.type_institution_id: {'id': i.id, 'nom': i.nom}
         for i in institutions}).replace('"', '\\"')
    return render(request, 'gestion/renseignements_personnels.html',
                  {'participant': participant, 'form': form,
                   'show_save_and_add_new_button': participant is None,
                   'fonctions': mark_safe(fonctions_json),
                   'institutions': mark_safe(institutions_json),
                   })


def ajout_participant(request):
    return modifier_renseignements_personnels(
        request, cancel_to_url=reverse('participants'))


def fiche_participant(request, id_participant):
    require_permission(request.user, consts.PERM_LECTURE)
    extrafields = [probleme['sql_expr']
                   for probleme in consts.PROBLEMES.values()]
    extrafields.extend((
        'frais_inscription', 'frais_inscription_facture',
        'frais_transport', 'frais_transport_facture',
        'frais_hebergement', 'frais_hebergement_facture',
        'forfaits_invites', 'frais_autres',
        'total_frais', 'total_facture', 'solde'
    ))
    participant = Participant.objects \
        .sql_extra_fields(*extrafields) \
        .select_related('etablissement', 'etablissement__region',
                        'etablissement__pays', 'inscription',
                        'fonction', 'hotel') \
        .get(pk=id_participant)
    renseignements_personnels = forms.RenseignementsPersonnelsForm(
        instance=participant)
    sejour_form = forms.SejourForm(participant=participant)
    transport_top = forms.TransportFormTop(instance=participant)
    transport_arrdep = forms.ArriveeDepartForm(participant=participant)
    transport_bottom = forms.TransportFormBottom(instance=participant)
    participation_activites = ParticipationActivite.objects.filter(
        participant=participant)
    facturation_form = forms.FacturationForm(instance=participant)
    prises_en_charge = []
    if participant.prise_en_charge_inscription:
        prises_en_charge.append(u"Frais d'inscription")
    if participant.prise_en_charge_sejour:
        if participant.a_forfait(consts.CODE_SUPPLEMENT_CHAMBRE_DOUBLE):
            prises_en_charge.append(u"Hébergement (supplément chambre double)")
        else:
            prises_en_charge.append(u"Hébergement")
    if participant.prise_en_charge_transport:
        prises_en_charge.append(u"Transport")
    if participant.prise_en_charge_activites:
        prises_en_charge.append(u"Activités")
    problemes = []
    for probleme in consts.PROBLEMES.values():
        sql_expr = probleme['sql_expr']
        if getattr(participant, sql_expr):
            problemes.append(probleme)
    if not request.user.is_staff:
        fichiers = participant.fichier_set.filter(efface_le=None)
    else:
        fichiers = participant.fichier_set.all()

    if participant.inscription_id:
        lien_dossier = reverse(
            'connexion_inscription',
            args=(participant.inscription.invitation.jeton, ))
    else:
        lien_dossier = None

    return render(request, 'gestion/fiche_participant.html', {
        'participant': participant,
        'participation_activites': participation_activites,
        'renseignements_personnels': renseignements_personnels,
        'sejour': sejour_form,
        'transport_top': transport_top,
        'transport_arrdep': transport_arrdep,
        'transport_bottom': transport_bottom,
        'facturation': facturation_form,
        'prises_en_charge': prises_en_charge,
        'perms_dict': consts.PERMS_DICT,
        'problemes': problemes,
        'fichiers': fichiers,
        'lien_dossier': lien_dossier,
    })


def renseignements_personnels_view(request, id_participant):
    return modifier_renseignements_personnels(
        request, id_participant=id_participant,
        cancel_to_url=reverse('fiche_participant', args=[id_participant]))


def tableau_de_bord(request):
    require_permission(request.user, consts.PERM_LECTURE)
    total_participants = Participant.objects.count()
    total_actifs = Participant.actifs.count()
    total_problematiques = Participant.actifs \
        .sql_filter('%s', 'problematique') \
        .count()
    par_probleme = [
        {
            'code': code,
            'libelle': probleme['libelle'],
            'nombre': Participant.actifs.sql_filter('%s',
                                                    probleme['sql_expr']
                                                    ).count()
        }
        for code, probleme in consts.PROBLEMES.items()
    ]
    par_fonction = []
    for fonction in Fonction.objects.all():
        nombre_clos = Participant.actifs.filter(
            fonction=fonction, suivi__code='doss_complet').count()
        nombre_ouverts = Participant.actifs.filter(fonction=fonction)\
            .exclude(suivi__code='doss_complet').count()
        par_fonction.append((
            fonction, nombre_clos, nombre_ouverts, nombre_clos + nombre_ouverts
        ))
    nb_invites = Invite.objects.filter(participant__desactive=False).count()
    hotels, types_chambres, donnees_hotels_par_jour, totaux_hotels = \
        get_donnees_hotels()
    nombres_votants, totaux_votants = get_nombre_votants_par_region()
    return render(
        request, 'gestion/tableau_de_bord.html',
        {
            'inscriptions_par_mois': get_inscriptions_par_mois(),
            'total_participants': total_participants,
            'total_actifs': total_actifs,
            'total_desactives': total_participants - total_actifs,
            'total_problematiques': total_problematiques,
            'par_probleme': par_probleme,
            'points_de_suivi':
            PointDeSuivi.objects.avec_nombre_participants().all(),
            'par_fonction': par_fonction,
            'nb_invites': nb_invites,
            'hotels': hotels,
            'types_chambres': types_chambres,
            'donnees_hotels_par_jour': donnees_hotels_par_jour,
            'totaux_hotels': totaux_hotels,
            'nombres_votants': nombres_votants,
            'totaux_votants': totaux_votants,
            'activites': get_donnees_activites(),
            'prises_en_charge': get_donnees_prise_en_charge(),
            'nb_tout_paye': Participant.actifs.filter(
                suivi__code="frais_payes"
            ).count(),
            'nb_tout_paye_droit_de_vote': Participant.actifs.filter(
                suivi__code="frais_payes", # statut__droit_de_vote=True
            ).count(),
        })


def notes_de_frais(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(request.user, consts.PERM_MODIF_NOTES_DE_FRAIS,
                       obj=participant)
    if request.method == 'GET':
        form = forms.NotesDeFraisForm(participant=participant)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        form = forms.NotesDeFraisForm(request.POST, participant=participant)
        if form.is_valid():
            form.save()
            return redirect('fiche_participant', id_participant)
    return render(request, 'gestion/notes_de_frais.html',
                  {'participant': participant,
                   'form': form, })


def sejour(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(request.user, consts.PERM_MODIF_SEJOUR, obj=participant)
    if request.method == 'GET':
        form = forms.SejourForm(participant=participant)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        form = forms.SejourForm(request.POST, participant=participant)
        if form.is_valid():
            form.save()
            return redirect('fiche_participant', id_participant)
    # on crée une structure qui contient les informations sur les
    # disponibilités des différents types de chambres dans les différents
    # hôtels.
    chambres_hotels = {}
    for hotel in Hotel.objects.all():
        chambres = hotel.chambres()
        for type_code, chambre in chambres.items():
            chambre["field_name"] = form.chambre_fields_by_type[type_code]
        chambres_hotels[hotel.id] = chambres
    return render(request, 'gestion/sejour.html',
                  {'participant': participant,
                   'form': form,
                   'chambres_hotels': json.dumps(chambres_hotels)})


def suivi_view(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(request.user, consts.PERM_MODIF_SUIVI, obj=participant)
    if request.method == 'GET':
        form = forms.SuiviForm(instance=participant)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        form = forms.SuiviForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            return redirect('fiche_participant', id_participant)
    return render(request, 'gestion/suivi.html',
                  {'participant': participant, 'form': form})


def transport(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(request.user, consts.PERM_MODIF_SEJOUR, obj=participant)
    if request.method == 'GET':
        form_top = forms.TransportFormTop(instance=participant, prefix='top')
        form_bottom = forms.TransportFormBottom(
            instance=participant, prefix='bottom'
        )
        form_arrivee_depart = forms.ArriveeDepartForm(
            participant=participant, prefix='arrdep'
        )
        formset_vols = forms.VolFormSet(instance=participant, prefix='vols')
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        form_top = forms.TransportFormTop(
            request.POST, instance=participant, prefix='top'
        )
        form_bottom = forms.TransportFormBottom(
            request.POST, instance=participant, prefix='bottom'
        )
        form_arrivee_depart = forms.ArriveeDepartForm(
            request.POST, participant=participant, prefix='arrdep'
        )
        formset_vols = forms.VolFormSet(
            request.POST, instance=participant, prefix='vols'
        )
        top_is_valid = form_top.is_valid()
        bottom_is_valid = form_bottom.is_valid()
        arrivee_depart_is_valid = form_arrivee_depart.is_valid()
        formset_vols_is_valid = formset_vols.is_valid()
        if top_is_valid and bottom_is_valid and arrivee_depart_is_valid \
                and formset_vols_is_valid:
            form_top.save()
            form_bottom.save()
            form_arrivee_depart.save()
            formset_vols.save()
            return redirect('fiche_participant', id_participant)
    return render(
        request, 'gestion/transport.html',
        {'participant': participant, 'form_top': form_top,
         'form_bottom': form_bottom,
         'form_arrivee_depart': form_arrivee_depart,
         'formset_vols': formset_vols})


def invites_view(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(
        request.user, consts.PERM_MODIF_RENSEIGNEMENTS_PERSONNELS,
        obj=participant
    )
    if request.method == 'GET':
        formset_invites = forms.InvitesFormSet(instance=participant)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        formset_invites = forms.InvitesFormSet(request.POST,
                                               instance=participant)
        if formset_invites.is_valid():
            formset_invites.save()
            return redirect('fiche_participant', id_participant)
    return render(request, 'gestion/invites.html',
                  {'participant': participant,
                   'formset_invites': formset_invites})


def facturation(request, id_participant):
    participant = Participant.objects.get(pk=id_participant)
    require_permission(request.user, consts.PERM_MODIF_FACTURATION,
                       obj=participant)
    if request.method == 'GET':
        form = forms.FacturationForm(instance=participant)
        paiement_formset = forms.PaiementFormset(instance=participant)
    else:
        assert request.method == 'POST'
        if 'annuler' in request.POST:
            return redirect('fiche_participant', id_participant)
        form = forms.FacturationForm(request.POST, instance=participant)
        paiement_formset = forms.PaiementFormset(request.POST,
                                                 instance=participant)
        if form.is_valid() and paiement_formset.is_valid():
            form.save()
            paiement_formset.save()
            return redirect('fiche_participant', id_participant)
    return render(request, 'gestion/facturation.html',
                  {'participant': participant,
                   'form': form, 'paiement_formset': paiement_formset})


def facture_pdf(request, id_participant):
    try:
        participant = Participant.objects \
            .sql_extra_fields(
                'frais_inscription_facture', 'frais_transport_facture',
                'frais_hebergement_facture', 'total_facture', 'solde'
            ).get(id=id_participant)
    except Participant.DoesNotExist:
        raise Http404
    return facture_response(participant)


def itineraire_pdf(request, id_participant):
    participant = Participant.objects.sql_extra_fields(
        'frais_autres').get(id=id_participant)
    filename = u'Itinéraire - %s %s.pdf' % (
        participant.prenom, participant.nom
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % \
                                      urllib.quote(filename.encode('utf-8'))
    return pdf.generer_itineraires(response, [participant])


def fichiers_view(request, id_participant):
    participant = Participant.objects.get(id=id_participant)
    require_permission(request.user, consts.PERM_MODIF_FICHIERS, 
                       obj=participant)
    if request.user.is_staff:
        fichiers = participant.fichier_set.all()
    else:
        fichiers = participant.fichier_set.filter(efface_le=None)
    if request.method == 'GET':
        form = forms.AjoutFichierForm(instance=participant)
    else:
        assert request.method == 'POST'
        if 'fichier_a_effacer' in request.POST:
            fichier_id = request.POST['fichier_a_effacer']
            try:
                fichier = Fichier.objects.get(id=fichier_id)
#                os.remove(os.path.join(
#                    settings.PATH_FICHIERS_PARTICIPANTS, fichier.filename()
#                ))
                fichier.efface_le = datetime.now()
                fichier.efface_par = request.user
                fichier.save()
            except Fichier.DoesNotExist:
                pass
            return redirect(reverse('fichiers', args=[id_participant]))
        else:
            fichier = Fichier(participant=participant,
                              cree_par=request.user)
            form = forms.AjoutFichierForm(
                request.POST, request.FILES,
                instance=fichier
            )
            if form.is_valid():
                form.save()
                return redirect(reverse('fichiers', args=[id_participant]))
    return render(request, 'gestion/fichiers.html', {
        'participant': participant,
        'fichiers': fichiers,
        'form': form
    })


def media_participant(request, nom_fichier):
    require_permission(request.user, consts.PERM_LECTURE)
    return sendfile(request, os.path.join(
        settings.PATH_FICHIERS_PARTICIPANTS, nom_fichier
    ))


def logout(request):
    auth_logout(request)
    return redirect('connexion')


def changement_mot_de_passe(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, u'Votre mot de passe a été changé.')
        return redirect('tableau_de_bord')
    return render(request, 'gestion/changement_mot_de_passe.html', {
        'form': form
    })


def supprimer_participant(request):
    id_participant = request.POST['id']
    participant = Participant.objects.get(id=id_participant)
    require_permission(request.user, consts.PERM_SUPPRESSION, obj=participant)
    participant.delete()
    return redirect('tableau_de_bord')


@user_passes_test(lambda u: u.is_staff)
def ajouter_vol_groupe(request):
    return modifier_vol_groupe(request, None)


@user_passes_test(lambda u: u.is_staff)
def modifier_vol_groupe(request, id_participant):
    if id_participant:
        vol_groupe = VolGroupe.objects.get(id=id_participant)
    else:
        vol_groupe = VolGroupe()
    if request.method == 'GET':
        form = forms.VolGroupeForm(instance=vol_groupe, prefix='top')
        formset = forms.VolGroupeFormSet(instance=vol_groupe, prefix='vols')
    else:
        assert request.method == 'POST'
        form = forms.VolGroupeForm(request.POST, instance=vol_groupe,
                                   prefix='top')
        formset = forms.VolGroupeFormSet(request.POST, instance=vol_groupe,
                                         prefix='vols')
        form_is_valid = form.is_valid()
        formset_is_valid = formset.is_valid()
        if form_is_valid and formset_is_valid:
            form.save()
            formset.save()
            return redirect(reverse('liste_vols_groupes'))
    return render(request, 'gestion/modifier_vol_groupe.html', {
        'vol_groupe': vol_groupe,
        'form': form,
        'formset': formset,
    })


def liste_vols_groupes(request):
    require_permission(request.user, consts.PERM_LECTURE)
    liste_vols = VolGroupe.objects.all()
    return render(request, 'gestion/liste_vols_groupes.html',
                  {'liste_vols': liste_vols})


@user_passes_test(lambda u: u.is_staff)
def supprimer_vol_groupe(request, id_vol):
    vol_groupe = VolGroupe.objects.get(id=id_vol)
    assert not vol_groupe.est_utilise()
    vol_groupe.delete()
    return redirect(reverse('liste_vols_groupes'))


def itineraire_view(request, id_itineraire):
    require_permission(request.user, consts.PERM_LECTURE)
    itineraire = InfosVol.objects.filter(vol_groupe__id=id_itineraire)
    prix_total = sum([vol.prix or 0 for vol in itineraire])
    return render(request, "gestion/table_itineraire.html", {
        "itineraire": itineraire,
        "prix_total": prix_total,
    })


def etats_listes(request):
    require_permission(request.user, consts.PERM_LECTURE)
    form_departs = forms.FiltresEtatArriveesForm(
        dates=donnees_etats.get_dates_departs(),
        auto_id=consts.DEPARTS + '_%s',
        initial={'arrivee_depart': consts.DEPARTS})
    form_arrivees = forms.FiltresEtatArriveesForm(
        dates=donnees_etats.get_dates_arrivees(),
        auto_id=consts.ARRIVEES + '_%s',
        initial={'arrivee_depart': consts.ARRIVEES})
    return render(request, 'gestion/etats_listes.html', {
        'form_departs': form_departs,
        'form_arrivees': form_arrivees
    })


def etat_inscrits(request):
    require_permission(request.user, consts.PERM_LECTURE)
    liste_inscrits = donnees_etats.get_donnees_etat_participants()
    maintenant = datetime.now()
    return render(request, 'gestion/etat_inscrits.html', {
        'liste_inscrits': liste_inscrits,
        'maintenant': maintenant
    })


def etat_activites(request):
    require_permission(request.user, consts.PERM_LECTURE)
    participants_activites = donnees_etats.get_donnees_participants_activites()
    maintenant = datetime.now()
    return render(
        request,
        'gestion/etat_activites.html', {
            'participants_activites': participants_activites,
            'maintenant': maintenant})


def etat_arrivees_departs(request):
    require_permission(request.user, consts.PERM_LECTURE)
    maintenant = datetime.now()
    if request.method == 'GET':
        if request.GET['arrivee_depart'] == consts.ARRIVEES:
            dates = donnees_etats.get_dates_arrivees()
        else:
            dates = donnees_etats.get_dates_departs()
        form = forms.FiltresEtatArriveesForm(data=request.GET, dates=dates)
        if form.is_valid():
            arrivees_departs = form.cleaned_data["arrivee_depart"]
            ville = form.cleaned_data["ville"]
            jour = datetime.strptime(form.cleaned_data["jour"], '%d/%m/%Y')
            donnees_arrivees_departs = \
                donnees_etats.get_donnees_arrivees_departs(
                    arrivees_departs, ville, jour)
            donnees_arrivees_departs.update({'maintenant': maintenant}) 
            return render(request,
                          'gestion/etat_arrivees_departs.html',
                          donnees_arrivees_departs)
        else:
            return redirect(reverse('etats_listes') + '?erreur_arrdep=1')
    else:
        return Http404()


def liste_participants_activites_scientifiques(request):
    require_permission(request.user, consts.PERM_LECTURE)
    donnees = donnees_etats.get_donnees_activites_scientifiques()
    return render(request, 'gestion/activites_scientifiques.html', {
        'donnees': donnees,
    })


def votants_csv(request):
    require_permission(request.user, consts.PERM_LECTURE)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="votants_ag.csv"'
    writer = csv.writer(response, delimiter=',', quotechar='"')
    participants = Participant.objects.avec_region_vote().filter_votants()
    writer.writerow([
        'participant_id', 'civilite', 'nom', 'prenom', 'courriel',
        'poste', 'fonction', 'etablissement_id', 'qualite', 'statut',
        'pays', 'region', 'region_vote', 'etablissement_nom'
    ])
    for participant in participants:
        etablissement = participant.etablissement
        row = [
            participant.id, participant.get_genre_display(),
            participant.nom, participant.prenom,
            participant.courriel, participant.poste,
            participant.fonction.libelle, participant.etablissement_id,
            etablissement.qualite, etablissement.statut,
            etablissement.pays.nom, etablissement.region.nom,
            participant.region_vote, etablissement.nom
        ]
        for index, value in enumerate(row):
            if isinstance(value, unicode):
                row[index] = value.encode("UTF-8")
        writer.writerow(row)
    return response


def etat_votants(request):
    require_permission(request.user, consts.PERM_LECTURE)
    votants = Participant.actifs.avec_region_vote().filter_votants()
    maintenant = datetime.now()
    votants = votants.order_by('nom', 'prenom')

    return render(request, 'gestion/etat_votants.html', {
        'votants': votants,
        'maintenant': maintenant
    })

TOUTES_VILLES = u'(Toutes)'


def etat_vols(request):
    require_permission(request.user, consts.PERM_LECTURE)
    ville_depart = request.GET.get('ville_depart', None)
    ville_arrivee = request.GET.get('ville_arrivee', None)
    ville_depart = None if ville_depart == TOUTES_VILLES else ville_depart
    ville_arrivee = None if ville_arrivee == TOUTES_VILLES else ville_arrivee
    return render(request, 'gestion/etat_vols.html', {
        'donnees': donnees_etats.get_donnees_tous_vols(
            filtre_ville_depart=ville_depart,
            filtre_ville_arrivee=ville_arrivee, ),
        'villes_depart': [TOUTES_VILLES] + donnees_etats.get_villes_depart(),
        'villes_arrivee': [TOUTES_VILLES] + donnees_etats.get_villes_arrivee(),
        'ville_depart': ville_depart,
        'ville_arrivee': ville_arrivee,
    })


def etat_vols_csv(request):
    require_permission(request.user, consts.PERM_LECTURE)
    now_str = datetime.now().strftime('%Y%m%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="etat_vols{0}.csv"'.format(now_str)
    writer = csv.writer(response, delimiter=',', quotechar='"')
    writer.writerow([
        "Date", "Heure", "Compagnie", "# vol", "Ville",
        "Type", "c", "Nom", "Prenom", "Direction", "Ville", "Date",
        "Vol Groupe", "PEC transport", "PEC sejour", "participant_id"])
    donnees = donnees_etats.get_donnees_tous_vols()
    for row in donnees:
        # noinspection PyProtectedMember
        row_dict = row._asdict().copy()
        for key, value in row_dict.iteritems():
            if key in ('prise_en_charge_sejour', 'prise_en_charge_transport'):
                row_dict[key] = "O" if row_dict[key] else "N"
            elif not row_dict[key]:
                row_dict[key] = ""
            elif isinstance(value, unicode):
                row_dict[key] = value.encode("UTF-8")
            elif key in ('date1', 'date2'):
                row_dict[key] = value.strftime('%d/%m/%Y')
            elif key == 'heure1':
                row_dict[key] = value.strftime('%H:%M')
        writer.writerow([
            row_dict['date1'], row_dict['heure1'], row_dict['compagnie'],
            row_dict['no_vol'], row_dict['ville1'], row_dict['dep_arr'],
            row_dict['genre'],  row_dict['nom'], row_dict['prenom'],
            row_dict['vers_de'], row_dict['ville2'], row_dict['date2'],
            row_dict['vol_groupe_nom'], row_dict['prise_en_charge_transport'],
            row_dict['prise_en_charge_sejour'], row_dict["participant_id"]
        ])
    return response


def bool_to_01(b):
    return "1" if b else "0"


def export_donnees_csv(request):
    require_permission(request.user, consts.PERM_LECTURE)
    now_str = datetime.now().strftime('%Y%m%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="donnees_ag_{0}.csv"'.format(now_str)
    writer = csv.writer(response, delimiter=',', quotechar='"')
    # response = HttpResponse(content_type='text/html')
    # response.write("<html><head></head><body>")
    fields = [
        "P_actif", "P_id", "P_genre", "P_nom", "P_prenom", "P_poste",
        "P_statut", "I_type", "E_cgrm", "E_qual", "E_statut",
        "I_nom", "I_pays", "I_region", "E_vote", "E_vote_region",
        "V_volACie", "V_volA", "V_dateA", "V_heureA",
        "V_volDCie", "V_volD", "V_dateD", "V_heureD", "H_id", "H_dateA",
        "H_dateD", "P_invite", "P_invite_nom", "AS_id", "PEC_t", "PEC_s",
        "vol_groupe", "P_courriel", "P_notes", "P_notes_statut", 
        "P_notes_facturation", "P_notes_transport", "P_remarques_transport",
        "P_notes_hebergement", "P_commentaires", "P_inscr_sur_place"]

    try:
        inscrits_sur_place = set(
            v[0] for v in
            PointDeSuivi.objects.get(code='inscr_sur_place')
            .participant_set.values_list('id'))
    except PointDeSuivi.DoesNotExist:
        inscrits_sur_place = set()
    activites = Activite.objects.all()
    for activite in activites:
        fields.append("act_{0}".format(activite.code))
    # attention l'ordre de avec_region_vote et select_related est important !
    participants = Participant.objects.order_by('nom', 'prenom') \
        .avec_region_vote()\
        .select_related('fonction', 'etablissement', 'etablissement__region',
                        'etablissement__pays', 'region', 'hotel', 'vol_groupe')
    # Écriture des en-têtes
    writer.writerow(fields)
    arrivees_vols_groupes = dict(
        (info.vol_groupe_id, info) for info in
        InfosVol.objects.filter(ville_arrivee='Marrakech',
                                type_infos=consts.VOL_GROUPE))
    departs_vols_groupes = dict(
        (info.vol_groupe_id, info) for info in
        InfosVol.objects.filter(ville_depart='Marrakech',
                                type_infos=consts.VOL_GROUPE))
    arrivees_autres = dict(
        (info.participant_id, info) for info in
        InfosVol.objects.filter(ville_arrivee='Marrakech')
        .exclude(type_infos=consts.VOL_GROUPE))
    departs_autres = dict(
        (info.participant_id, info) for info in
        InfosVol.objects.filter(ville_depart='Marrakech')
        .exclude(type_infos=consts.VOL_GROUPE))
    invites_participants = defaultdict(list)
    for invite in Invite.objects.all():
        invites_participants[invite.participant_id].append(invite)
    activites_participants = {}
    for part_activite in ParticipationActivite.objects\
            .select_related('activite'):
        key = (part_activite.participant_id, part_activite.activite.code)
        activites_participants[key] = part_activite
    for p in participants:
        row = SortedDict([(field, "") for field in fields])
        row['P_actif'] = bool_to_01(not p.desactive)
        row['P_id'] = p.id
        row['P_genre'] = p.genre
        row['P_nom'] = p.nom
        row['P_prenom'] = p.prenom
        row['P_poste'] = p.poste
        row['P_fonction'] = p.fonction.code
        row['E_vote'] = bool_to_01(p.region_vote)
        row['E_vote_region'] = p.region_vote
        row['I_type'] = p.type_institution
        if p.type_institution == Participant.ETABLISSEMENT:
            row['E_cgrm'] = p.etablissement.id
            row['E_qual'] = p.etablissement.qualite
            row['E_statut'] = p.etablissement.statut
            row['I_nom'] = p.etablissement.nom
            row['I_pays'] = p.etablissement.pays.code
            row['I_region'] = p.etablissement.region.code
        else:
            if p.pays_autre_institution:
                row['I_pays'] = p.pays_autre_institution.code
            if p.type_institution == Participant.INSTANCE_AUF:
                row['I_nom'] = p.get_instance_auf_display()
                row['I_region'] = p.get_region().code if p.get_region() else ""
            elif p.type_institution == Participant.AUTRE_INSTITUTION:
                row['I_type'] = p.type_institution
                row['I_nom'] = p.nom_autre_institution
        if p.vol_groupe_id:
            arrivee = arrivees_vols_groupes[p.vol_groupe_id]
            depart = departs_vols_groupes[p.vol_groupe_id]
        else:
            arrivee = arrivees_autres.get(p.id, None)
            depart = departs_autres.get(p.id, None)
        if arrivee:
            row["V_volA"] = arrivee.numero_vol
            row["V_volACie"] = arrivee.compagnie
            if arrivee.date_arrivee:
                row["V_dateA"] = arrivee.date_arrivee.strftime('%d/%m/%Y')
            if arrivee.heure_arrivee:
                row["V_heureA"] = arrivee.heure_arrivee.strftime('%H:%M')
        if depart:
            row["V_volD"] = depart.numero_vol
            row["V_volDCie"] = depart.compagnie
            if depart.date_depart:
                row["V_dateD"] = depart.date_depart.strftime('%d/%m/%Y')
            if depart.heure_depart:
                row["V_heureD"] = depart.heure_depart.strftime('%H:%M')
        if p.hotel:
            row["H_id"] = p.hotel.id
            if p.date_arrivee_hotel:
                row["H_dateA"] = p.date_arrivee_hotel.strftime('%d/%m/%Y')
            if p.date_depart_hotel:
                row["H_dateD"] = p.date_depart_hotel.strftime('%d/%m/%Y')
        invites = invites_participants[p.id]
        row["P_invite"] = len(invites)
        row["P_invite_nom"] = ','.join([i.nom_complet for i in invites])
        if p.activite_scientifique:
            row["AS_id"] = p.activite_scientifique.code
        for activite in activites:
            key = (p.id, activite.code)
            part_activite = activites_participants.get(key, None)
            if not part_activite:
                nb_personnes = 0
            else:
                nb_personnes = 1 + (len(invites) if part_activite.avec_invites
                                    else 0)
            row["act_{0}".format(activite.code)] = nb_personnes
        row["PEC_t"] = bool_to_01(p.prise_en_charge_transport)
        row["PEC_s"] = bool_to_01(p.prise_en_charge_sejour)
        row["vol_groupe"] = p.vol_groupe.nom if p.vol_groupe_id else ""
        row["P_courriel"] = p.courriel
        row["P_notes"] = p.notes
        row["P_notes_statut"] = p.notes_statut
        row["P_notes_facturation"] = p.notes_facturation
        row["P_notes_transport"] = p.notes_transport
        row["P_remarques_transport"] = p.remarques_transport
        row["P_notes_hebergement"] = p.notes_hebergement
        row["P_commentaires"] = p.commentaires
        row["P_inscr_sur_place"] = bool_to_01(p.id in inscrits_sur_place)
        encode_csv_row(row)
        writer.writerow(row.values())
    # response.write("</body></html>")
    return response


def etat_paiements(request):
    require_permission(request.user, consts.PERM_LECTURE)
    donnees = donnees_etats.get_donnees_paiements(actifs_seulement=True)
    return render(request, 'gestion/etat_paiements.html', {
        'donnees': donnees,
    })


def etat_paiements_csv(request):
    require_permission(request.user, consts.PERM_LECTURE)
    now_str = datetime.now().strftime('%Y%m%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="paiements_ag_{0}.csv"'.format(now_str)
    writer = csv.writer(response, delimiter=',', quotechar='"')
    fields = (
        'P_actif', 'P_id', 'P_genre', 'P_nom', 'P_prenom', 'P_poste',
        'P_courriel', 'P_adresse', 'P_ville', 'P_pays', 'P_code_postal',
        'P_telephone', 'P_telecopieur', 'P_fonction', 'E_cgrm', 'E_nom',
        'E_delinquant', 'P_invites', 'f_PEC_I', 'f_total_I', 'f_fact_I',
        'f_PEC_T', 'f_AUF_T', 'f_total_T', 'f_fact_T', 'f_PEC_S', 'f_AUF_S',
        'f_total_S', 'f_fact_S', 'f_supp_S', 'f_PEC_A', 'f_total_A', 'f_fact_A',
        'f_valide', 'f_mode', 'f_accompte', 'n_R', 'n_N', 'n_T', 'n_A',
        'n_mode', 'n_statut',)
    writer.writerow(fields)
    for p in donnees_etats.get_donnees_paiements(actifs_seulement=False):
        row = SortedDict([(field, "") for field in fields])
        for field in fields:
            row[field] = getattr(p, field)
        encode_csv_row(row)
        writer.writerow(row.values())
    return response


def encode_csv_row(row):
    for key, value in row.iteritems():
        if isinstance(value, basestring):
            value = value.replace('\n', ' ').replace('\r', ' ')
        if isinstance(value, unicode):
            value = value.encode("UTF-8")
        row[key] = value
