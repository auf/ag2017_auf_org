# encoding: utf-8
import collections
import datetime
import json
import time

from auf.django.mailing.models import Enveloppe, ModeleCourriel
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.db import transaction
from django.db.utils import IntegrityError
from django.dispatch import Signal
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ag.inscription.models import (
    Inscription, get_infos_montants, Invitation, InvitationEnveloppe,
    PaiementPaypal,
    PDTInvalide)
from ag.inscription.forms import (
    AccueilForm, RenseignementsPersonnelsForm, ProgrammationForm,
    TransportHebergementForm, PaiementForm, InscriptionForm,
    PaypalNotificationForm, PAYPAL_DATE_FORMATS
)

inscription_confirmee = Signal()

# noinspection PyUnresolvedReferences
import ag.gestion.notifications  # NOQA


def inscriptions_terminees():
    return datetime.date.today() >= settings.DATE_FERMETURE_INSCRIPTIONS


class Etape(object):

    def __init__(self, processus, donnees_etape):
        self.__dict__.update(donnees_etape)
        self.processus = processus

    def est_derniere_visible(self):
        return self.processus.est_derniere_visible(self)

    def est_derniere(self):
        return self.processus.est_derniere(self)

    def __str__(self):
        return '<etape %s>' % getattr(self, 'url_title', '?')

    def __unicode__(self):
        return self.__str__()

ETAPES_INSCRIPTION = (
    {
        "n": 0,
        "url_title": "accueil",
        "label": u"Accueil",
        "template": "accueil.html",
        "form_class": AccueilForm,
        "tab_visible": True,
    },
    {
        "n": 1,
        "url_title": "renseignements-personnels",
        "label": u"Participant",
        "template": "renseignements_personnels.html",
        "form_class": RenseignementsPersonnelsForm,
        "tab_visible": True,
    },
    {
        "n": 2,
        "url_title": "programmation",
        "label": u"Programmation",
        "template": "programmation.html",
        "form_class": ProgrammationForm,
        "tab_visible": True,
    },
    {
        "n": 3,
        "url_title": "transport-hebergement",
        "label": u"Séjour",
        "template": "transport_hebergement.html",
        "form_class": TransportHebergementForm,
        "tab_visible": True,
    },
    {
        "n": 4,
        "url_title": "paiement",
        "label": u"Modalités",
        "template": "paiement.html",
        "form_class": PaiementForm,
        "tab_visible": True,
#            "etape_class": EtapePaiement,
    },
    {
        "n": 5,
        "url_title": "apercu",
        "label": u"Aperçu",
        "template": "apercu.html",
        "form_class": None,
        "tab_visible": True,
#            "etape_class": EtapeApercu,
    },
    {
        "n": 6,
        "url_title": "confirmation",
        "label": u"Confirmation",
        "template": "confirmation.html",
        "form_class": None,
        "tab_visible": True,
    },
)


class EtapesProcessus(list):

    def __init__(self, **kwargs):
        donnees_etapes = kwargs.pop('donnees_etapes', ETAPES_INSCRIPTION)
        super(EtapesProcessus, self).__init__(self, **kwargs)
        for donnees_etape in donnees_etapes:
            self.append(Etape(self, donnees_etape))

    def etape_par_url(self, url_title):
        for etape in self:
            if etape.url_title == url_title:
                return etape
        raise Http404('Aucune page ne porte le titre "%s".' % url_title)

    def etape_suivante(self, etape_courante):
        for etape in self:
            if etape.n == etape_courante.n + 1:
                return etape

    def est_derniere_visible(self, une_etape):
        for etape in self:
            if etape.n > une_etape.n and etape.tab_visible:
                return False
        return True

    def est_derniere(self, une_etape):
        for etape in self:
            if etape.n > une_etape.n:
                return False
        return True

    def redirect_etape_suivante(self, etape_courante):
        etape_suivante = self.etape_suivante(etape_courante)
        return redirect('processus_inscription', etape_suivante.url_title)


def index(request):
    form = InscriptionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('processus_inscription', 'accueil')
    response = render(request, 'inscription/index.html', {
        'form': form,
    })
    request.session['django_language'] = 'fr'
    return response


def connexion_inscription(request, jeton):
    invitation = get_object_or_404(Invitation, jeton=jeton)
    try:
        inscription = Inscription.objects.get(invitation=invitation)
        if inscription.fermee or not inscriptions_terminees():
            request.session['inscription_id'] = inscription.id
        else:
            return redirect('inscriptions_terminees')
    except Inscription.DoesNotExist:
        if not inscriptions_terminees():
            inscription = Inscription(invitation=invitation)
            inscription.preremplir()
            inscription.save()
            request.session['inscription_id'] = inscription.id
        else:
            return redirect('inscriptions_terminees')
    return redirect('processus_inscription', 'accueil')


def get_paypal_context(request, inscription_id):
    return {
        'paypal_cancel': request.GET.get('paypal_cancel', False),
        'paypal_tx': request.GET.get('paypal_tx', None),
        'paypal_url': settings.PAYPAL_URL,
        'paypal_email_address': settings.PAYPAL_EMAIL_ADDRESS,
        'paypal_return_url': request.build_absolute_uri(reverse(
            'paypal_return', args=(inscription_id,)
        )),
        'paypal_notify_url': request.build_absolute_uri(
            reverse('paypal_ipn')
        ),
        'paypal_cancel_url': request.build_absolute_uri(
            reverse('paypal_cancel')
        ),
    }


def get_montants_context():
    toutes_infos_montants = get_infos_montants()
    return {
        'montants': toutes_infos_montants,
        'montants_json': json.dumps(dict(
            (code, infos_montant.__dict__)
            for code, infos_montant in toutes_infos_montants.iteritems()
        )),
    }


AppelEtapeProcessus = collections.namedtuple(
    'AppelEtapeProcessus',
    ('etapes_processus', 'etape_courante', 'request',
     'inscription'))


def redirect_etape(url_title):
    return redirect('processus_inscription', url_title)


def appel_apercu(appel_etape_processus):
    request = appel_etape_processus.request
    if request.method == 'POST':
        if 'modifier' in request.POST:
            return redirect_etape('renseignements-personnels')
        else:
            return redirect_etape_suivante(appel_etape_processus)


def redirect_etape_suivante(appel_etape_processus):
        return appel_etape_processus.etapes_processus\
            .redirect_etape_suivante(appel_etape_processus.etape_courante)


def processus_inscription(request, url_title=None):
    etapes_processus = EtapesProcessus()
    etape_courante = etapes_processus.etape_par_url(url_title)

    request.session['django_language'] = 'fr'
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('info_inscription')
    inscription = get_object_or_404(Inscription, id=inscription_id)

    appel_etape_processus = AppelEtapeProcessus(
        etapes_processus=etapes_processus, etape_courante=etape_courante,
        inscription=inscription, request=request)

    if inscription.fermee and url_title != 'confirmation':
        return redirect_etape('confirmation')

    if url_title == 'apercu':
        redir = appel_apercu(appel_etape_processus)
    elif url_title == 'confirmation':
        if not inscription.fermee:
            inscription.fermer()
            inscription_confirmee.send_robust(inscription)

    form_class = etape_courante.form_class
    if form_class:
        form = form_class(request.POST or None, instance=inscription)
        form.require_fields()
        if request.method == "POST" and form.is_valid():
            form.save()
            return redirect_etape_suivante(appel_etape_processus)
    else:
        form = None

    context = {
        'form': form,
        'inscription': inscription,
        'etape_courante': etape_courante,
        'etapes': etapes_processus,
    }

    if url_title in ('confirmation', 'apercu'):
        context.update(get_paypal_context(request, inscription_id))

    if url_title == 'programmation':
        context.update(get_montants_context())

    if url_title == 'confirmation':
        context['inscriptions_terminees'] = inscriptions_terminees()

    return render(request, 'inscription/' + etape_courante.template, context)


@require_POST
def ajout_invitations(request):
    inscription_id = request.session.get('inscription_id', None)
    if not inscription_id:
        return redirect('connexion_inscription')
    inscription = Inscription.objects.get(id=inscription_id)
    if (inscription.fermee and inscription.est_pour_mandate() and
            not inscriptions_terminees()):
        liste_adresses_text = request.POST['liste_adresses']
        liste_adresses = liste_adresses_text.splitlines()
        modele_courriel = ModeleCourriel.objects.get(code='acc')
        for adresse in liste_adresses:
            try:
                validate_email(adresse)
                if not Invitation.objects.filter(courriel=adresse).count():
                    enveloppe = Enveloppe(modele=modele_courriel)
                    enveloppe.save()
                    invitation = Invitation(
                        courriel=adresse, pour_mandate=False,
                        etablissement=inscription.get_etablissement()
                    )
                    invitation.save()
                    invitation_enveloppe = InvitationEnveloppe(
                        invitation=invitation, enveloppe=enveloppe
                    )
                    invitation_enveloppe.save()
            except ValidationError:
                pass
    return redirect(
        reverse('processus_inscription', args=['confirmation']) + '#invitation'
    )


def save_paiement(paiement):
    try:
        paiement.save()
        paiement.notifier()
        transaction.commit()
    except IntegrityError:
        # il peut y avoir une "race condition" entre PDT et IPN et dans ce cas,
        # il se pourrait que la contrainte d'unicité sur
        # PaiementPaypal.numero_transaction soit violée. Si cela arrive on
        # recharge l'objet
        transaction.rollback()
        paiement_existant = PaiementPaypal.objects.get(
            numero_transaction=paiement.numero_transaction
        )
        if not paiement_existant.est_complet() and paiement.est_complet():
            # si la validation du paiement a échoué précédemment,
            # mais a réussi cette fois-ci, on enregistre la réussite
            paiement.id = paiement_existant.id
            paiement.save()
            paiement.notifier()
            transaction.commit()
        else:
            transaction.rollback()


def paypal_return(request, id_):
    inscription = get_object_or_404(Inscription, id=id_)
    inscription.paiement = 'CB'
    inscription.save()
    numero_transaction = request.GET.get('tx', None)
    try:
        paiement = PaiementPaypal.objects.get(
            numero_transaction=numero_transaction
        )
    except PaiementPaypal.DoesNotExist:
        paiement = PaiementPaypal()
        paiement.numero_transaction = numero_transaction
    try:
        with transaction.atomic():
            if not paiement.pdt_valide:
                d = paiement.verifier_pdt()
                paiement.inscription = inscription
                paiement.montant = d.get('mc_gross', None)
                paiement.devise = d.get('mc_currency', None)
                paiement.statut = d.get('payment_status', None)
                paiement.raison_attente = d.get('pending_reason', None)
                payment_date = d.get('payment_date', None)
                if payment_date:
                    for date_format in PAYPAL_DATE_FORMATS:
                        try:
                            paiement.date_heure = datetime.datetime(
                                *time.strptime(payment_date, date_format)[:6]
                            )
                        except ValueError:
                            continue
                save_paiement(paiement)
            else:
                raise PDTInvalide()
    except PDTInvalide:
        pass
    if paiement.numero_transaction:
        return redirect(
            reverse('processus_inscription', args=['confirmation']) +
            '?paypal_tx=' + paiement.numero_transaction
        )
    else:
        return redirect('processus_inscription', 'paiement')


@csrf_exempt
@require_POST
# @commit_manually
def paypal_ipn(request):
    def form_to_paiement(form, paiement):
        paiement.montant = form.cleaned_data['mc_gross']
        paiement.devise = form.cleaned_data['mc_currency']
        paiement.statut = form.cleaned_data['payment_status']
        paiement.raison_attente = form.cleaned_data['pending_reason']
        paiement.date_heure = form.cleaned_data['payment_date']

    try:
        assert request.method == 'POST'
        form = PaypalNotificationForm(request.POST)
        if form.is_valid():
            numero_transaction = form.cleaned_data['txn_id']
            try:
                paiement = PaiementPaypal.objects.get(
                    numero_transaction=numero_transaction
                )
            except PaiementPaypal.DoesNotExist:
                paiement = PaiementPaypal()
                paiement.numero_transaction = numero_transaction
            paiement.ipn_post_data = request.raw_post_data
            paiement.verifier_ipn(request)
            id_inscription = form.cleaned_data['invoice']
            inscription = Inscription.objects.get(id=id_inscription)
            paiement.inscription = inscription
            form_to_paiement(form, paiement)
            save_paiement(paiement)
        else:
            transaction.rollback()
        return HttpResponse("OK")
    except:
        transaction.rollback()
        raise


def paypal_cancel(request):
    return redirect(
        reverse(
            'processus_inscription', args=['paiement']
        ) + "?paypal_cancel=1"
    )
