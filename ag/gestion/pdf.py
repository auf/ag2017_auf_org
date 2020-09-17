# encoding: utf-8

import os
import urllib.request, urllib.parse, urllib.error
from collections import namedtuple
from datetime import date
from django.http import HttpResponse
from django.utils.dateformat import time_format
from django.utils.formats import date_format
from reportlab.lib.colors import black, lightgrey
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Paragraph, Table, TableStyle, Spacer

from ag.gestion import APP_ROOT
from ag.inscription.models import Inscription, montant_str

PAGESIZE = letter

Facture = namedtuple('Facture',
                     ('titre', 'civilite', 'nom', 'prenom', 'numero_facture',
                      'numero', 'date_facturation', 'adresse',
                      'etablissement_id', 'numero_dossier', 'imputation',
                      'frais_inscription', 'frais_forfaits',
                      'frais_hebergement', 'total_frais',
                      'paiements', 'verse_en_trop', 'solde_a_payer', 'validee'))


def get_renseignement_personnels_fields(rp):
    """

    :param rp: ag.inscription.models.RenseignementsPersonnels
    :return:
    """
    return {
        'civilite': rp.get_genre_display(),
        'nom': rp.nom,
        'prenom': rp.prenom,
        'adresse': rp.get_adresse(),
        'titre': titre_facture(rp)
    }


def titre_facture(inscription_ou_participant):
    obj = inscription_ou_participant
    if obj.total_deja_paye == 0:
        return "Facture"
    elif obj.get_verse_en_trop() or obj.get_solde_a_payer():
        return "État de compte"
    else:
        return "Reçu"


def facture_from_participant(participant):
    """

    :param participant:
    :return:
    """
    rp_dict = get_renseignement_personnels_fields(participant)
    inscription = participant.inscription
    return Facture(
        numero_facture=None,
        date_facturation=participant.inscription.date_fermeture
        if inscription else None,
        numero=participant.numero,
        etablissement_id=participant.etablissement_id,
        numero_dossier=inscription.numero_dossier if inscription else None,
        imputation=None,
        frais_inscription=participant.frais_inscription_facture,
        frais_forfaits=participant.forfaits_invites,
        frais_hebergement=participant.frais_hebergement_facture,
        total_frais=participant.total_facture,
        paiements=participant.get_paiements_display(),
        verse_en_trop=participant.get_verse_en_trop(),
        solde_a_payer=participant.get_solde_a_payer(),
        validee=False,
        **rp_dict
    )


def facture_from_inscription(inscription):
    """

    :param inscription: ag.inscription.models.Inscription
    :return:
    """
    rp_dict = get_renseignement_personnels_fields(inscription)
    return Facture(
        numero_facture=None,
        date_facturation=inscription.date_fermeture,
        numero=inscription.numero,
        etablissement_id=inscription.get_etablissement().id,
        numero_dossier=inscription.numero_dossier,
        imputation=None,
        frais_inscription=inscription.get_frais_inscription(),
        frais_forfaits=inscription.get_total_forfaits_suppl(),
        frais_hebergement=inscription.get_frais_hebergement(),
        total_frais=inscription.get_montant_total(),
        paiements=inscription.get_paiements_display(),
        verse_en_trop=inscription.get_verse_en_trop(),
        solde_a_payer=inscription.get_solde_a_payer(),
        validee=False,
        **rp_dict
    )


# noinspection PyTypeChecker
def generer_factures(output_file, factures):
    """

    :param output_file: File
    :param factures: List[Facture]
    :return:
    """

    # Dimensions
    page_width, page_height = PAGESIZE
    margin_top = margin_left = margin_right = 2 * cm
    frame_width = page_width - margin_left - margin_right

    # Styles
    styles = StyleSheet()
    styles.add_style('normal')
    styles.add_style(
        'titre', fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER
    )
    styles.add_style('sous-titre', fontSize=8, alignment=TA_CENTER)
    styles.add_style(
        'destinataire', fontName='Helvetica-Bold', alignment=TA_CENTER
    )
    styles.add_style('petit', fontSize=8)
    styles.add_style('droite', alignment=TA_RIGHT)

    canvas = Canvas(output_file, pagesize=PAGESIZE)
    for facture in factures:

        # Préparation de certaines chaînes
        nom_participant = ' '.join((
            facture.civilite, facture.prenom,
            facture.nom
        ))
        if facture.numero_facture:
            numero_facture = "-%02d" % facture.numero_facture
        else:
            numero_facture = None
        if facture.date_facturation:
            date_facturation = date_format(facture.date_facturation,
                                           'SHORT_DATE_FORMAT')
        else:
            date_facturation = ""
        adresse = facture.adresse

        # Logos
        logo_height = 80
        logo_width = 300 * logo_height / 143
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'agauflogo2017.jpg'),
            margin_left, page_height - margin_top - logo_height,
            logo_width, logo_height
        )

        # Adresse de l'AUF
        x = margin_left + logo_width
        y = page_height - margin_top - 16
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(x, y, "Secrétariat de l'assemblée générale")
        y -= 12
        canvas.setFont('Helvetica', 8)
        for s in [
            "Case postale du Musée C.P. 49714",
            "Montréal (Québec), H3T 2A5, Canada",
            "Courriel : ag2017@auf.org",
            "Site : www.ag2017.auf.org",
        ]:
            canvas.drawString(x, y, s)
            y -= 10

        # Titre
        y -= 2 * cm
        x = margin_left
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(x, y, facture.titre)

        # Adresse
        y -= 1.5 * cm
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(x, y - 10, "Pour:")

        x += 1.5 * cm
        canvas.setFont('Helvetica', 10)
        p = Paragraph('<br/>'.join([
            nom_participant,
            adresse.adresse,
            adresse.ville,
            adresse.code_postal,
            adresse.pays,
        ]), styles['normal'])
        w, h = p.wrap(8 * cm, 5 * cm)
        p.drawOn(canvas, x, y - h)

        # Autres infos
        x += 8 * cm
        t = Table(
            [
                ["Date d'émission", date_facturation] if date_facturation
                else ["", ""],
                ["# Facture", "{}-{}".format(
                    facture.numero,
                    [numero_facture] if numero_facture else "00")],
                ["# Dossier", facture.numero_dossier],
                [
                    "# Membre",
                    "CGRM{}".format(
                        facture.etablissement_id)
                    if facture.etablissement_id else ""
                ],
                ["# Imputation", "70810." + facture.imputation]
                if facture.imputation else [],
            ],
            colWidths=(4 * cm, 4 * cm),
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), lightgrey),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ])
        )
        w, h = t.wrap(5 * cm, 5 * cm)
        t.drawOn(canvas, x, y - h + 3)

        # Détails
        x = margin_left
        y -= 4 * cm
        t = Table(
            [
                ["Détails"],
                [
                    "Frais de participation à la 17e assemblée générale - "
                    "Marrakech (Maroc) - 9 au 11 mai 2017"
                ],
                [
                    "- Frais d'inscription",
                    montant_str(facture.frais_inscription)
                ],
                [
                    "- Forfaits supplémentaires",
                    montant_str(facture.frais_forfaits)
                ],
            ] +
            (
                [[
                    "- Frais de supplément chambre double",
                    montant_str(facture.frais_hebergement)
                ]]
                if facture.frais_hebergement else []
            ) +
            [
                [
                    "",
                    "Montant total: " + montant_str(facture.total_frais)
                ],
            ],
            colWidths=(12 * cm, frame_width - 12 * cm),
            style=TableStyle([
                ('SPAN', (0, 0), (1, 0)),
                ('SPAN', (0, 1), (1, 1)),
                ('BOX', (0, 0), (-1, -1), 0.5, black),
                ('LINEBELOW', (0, 0), (1, 0), 0.5, black),
                ('BOTTOMPADDING', (0, 1), (1, 1), 0.5 * cm),
                ('BOTTOMPADDING', (0, -2), (1, -2), 0.5 * cm),
                ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, 0), (0, 1), 'Helvetica', 12),
                ('BACKGROUND', (-1, -1), (-1, -1), lightgrey),
            ])
        )
        w, h = t.wrap(frame_width, 10 * cm)
        t.drawOn(canvas, x, y - h)

        if facture.paiements:
            lignes_paiement = [["Paiements reçus"]]
            lignes_paiement.extend(
                [[p.date, p.moyen, p.implantation, p.ref_paiement, p.montant]
                 for p in facture.paiements])
            t = Table(
                lignes_paiement,
                colWidths=(2 * cm, 5 * cm, 2 * cm, 5 * cm,
                           frame_width - 14 * cm),
                style=TableStyle([
                    ('SPAN', (0, 0), (3, 0)),
                    ('BOX', (0, 0), (-1, -1), 0.5, black),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.5, black),
                    # ('BOTTOMPADDING', (0, 0), (-1, 0), 0.5 * cm),
                    # ('BOTTOMPADDING', (0, -2), (-1, -2), 0.5 * cm),
                    ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica', 12),
                    ('BACKGROUND', (-1, -1), (-1, -1), lightgrey),
                ]))
            x = margin_left
            y -= h + 0.75 * cm
            w, h = t.wrap(frame_width, 10 * cm)
            t.drawOn(canvas, x, y - h)

        y -= h + 0.75 * cm
        if facture.verse_en_trop:
            solde_text = "Versé en trop: " + montant_str(facture.verse_en_trop)
        else:
            solde_text = "Solde à payer: " + montant_str(facture.solde_a_payer)
        p = Paragraph(solde_text,
                      styles['droite'])
        _, h = p.wrap(frame_width, 2 * cm)
        p.drawOn(canvas, x, y)
        if facture.verse_en_trop:
            y -= h + 0.5 * cm
            p = Paragraph(
                """Votre remboursement s’effectuera automatiquement dans les
                prochains 30 jours utilisant la même méthode et versé même
                compte du paiement initial.
                """, styles['petit'])
            _, h = p.wrap(frame_width, 2 * cm)
            p.drawOn(canvas, x, y)

        # Rendu
        canvas.showPage()

    canvas.save()
    return output_file


def generer_itineraires(output_file, participants):
    # Dimensions
    page_width, page_height = PAGESIZE
    margin_top = margin_bottom = 1 * cm
    margin_left = margin_right = 1.5 * cm
    frame_width = page_width - margin_left - margin_right
    frame_height = page_height - margin_top - margin_bottom

    # Styles
    styles = StyleSheet()
    styles.add_style('normal', fontName='Helvetica', fontSize=11)
    styles.add_style('petit', fontName='Helvetica', fontSize=10)
    styles.add_style('bold', fontName='Helvetica-bold', fontSize=11)
    styles.add_style('titre', fontName='Helvetica-Bold', fontSize=15)
    styles.add_style('sous-titre', fontName='Helvetica-Bold', fontSize=11)
    styles.add_style('right-aligned', alignment=TA_RIGHT)
    styles.add_style('section', fontName='Helvetica-Bold', fontSize=12)
    styles.add_style('itineraire-header', fontName='Helvetica-Bold', fontSize=8)
    styles.add_style('itineraire', fontSize=8)
    styles.add_style('remarque', fontName='Helvetica-Oblique', fontSize=10)
    styles.add_style('bullet', bulletIndent=18, fontSize=11)
    styles.add_style(
        'important', borderWidth=1, borderRadius=3, borderColor=black,
        borderPadding=3, alignment=TA_CENTER, fontName='Helvetica-Bold',
        fontSize=11
    )

    canvas = Canvas(output_file, pagesize=PAGESIZE)
    for participant in participants:

        # Préparation
        contenu = []
        vols = participant.itineraire()
        nom_participant = ' '.join((
            participant.get_genre_display(), participant.prenom,
            participant.nom
        ))
        # Logos
        logo_height = 80
        logo_width = 300 * logo_height / 143
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'agauflogo2017.jpg'),
            margin_left, page_height - margin_top - logo_height,
            logo_width, logo_height
        )

        # Adresse de l'AUF
        x = margin_left + logo_width
        y = page_height - margin_top - 16
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(x, y, "Secrétariat de l'assemblée générale")
        y -= 12
        canvas.setFont('Helvetica', 8)
        for s in [
            "Case postale du Musée C.P. 49714",
            "Montréal (Québec), H3T 2A5, Canada",
            "Courriel : ag2017@auf.org",
            "Site : www.ag2017.auf.org",
        ]:
            canvas.drawString(x, y, s)
            y -= 10
        contenu.append(Spacer(0, 2.5 * cm))

        # Titre
        contenu.append(Paragraph(
            "Imprimé le " + date_format(date.today(), 'SHORT_DATE_FORMAT'),
            styles['right-aligned']))
        contenu.append(Spacer(0, 0.5 * cm))

        contenu.append(Paragraph("VOTRE ITINÉRAIRE DE VOYAGE - "
                                 "Assemblée générale AUF 2017",
                                 styles['titre']))
        contenu.append(Spacer(0, 0.5 * cm))

        # Coordonnées
        contenu.append(Table(
            [
                ["Passager :", nom_participant],
                ["Réservation :", participant.numero_dossier_transport],
                ["Institution :", participant.nom_institution()],
                ["Téléphone :", participant.telephone],
                ["Télécopieur :", participant.telecopieur],
                ["Courriel :", participant.courriel],
                # [u"Bureau régional AUF :",
                # participant.get_nom_bureau_regional()],
            ],
            colWidths=(5 * cm, 13.5 * cm),

            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 0, black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (0, -1), lightgrey),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8),
            ])
            ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Itinéraire
        contenu.append(Paragraph("Plan de vol :", styles['section']))
        contenu.append(Spacer(0, 0.25 * cm))
        contenu.append(Table(
            [[
                 Paragraph(header, styles['itineraire-header'])
                 for header in [
                     "Compagnie aérienne", "Numéro de vol",
                     "Ville de départ", "Date de départ",
                     "Heure départ", "Ville d'arrivée",
                     "Date arrivée", "Heure d'arrivée"
                 ]
                 ]] +
            [
                [
                    Paragraph(s, styles['itineraire'])
                    for s in [
                        vol.compagnie,
                        vol.numero_vol,
                        vol.ville_depart,
                        date_format(vol.date_depart, 'SHORT_DATE_FORMAT')
                        if vol.date_depart else '',
                        time_format(vol.heure_depart, 'H:i')
                        if vol.heure_depart else '',
                        vol.ville_arrivee,
                        date_format(vol.date_arrivee, 'SHORT_DATE_FORMAT')
                        if vol.date_arrivee else '',
                        time_format(vol.heure_arrivee, 'H:i')
                        if vol.heure_arrivee else '',
                    ]
                    ]
                for vol in vols
                ],
            colWidths=(
                2.5 * cm, 2 * cm, 3 * cm, 2 * cm, 2 * cm, 3 * cm,
                2 * cm, 2 * cm
            ),
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, black),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, black),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ])

            ))
        contenu.append(Table(
            [
                ["Retrait des titres de transport :", 
                 participant.get_modalite_retrait_billet_display()],
                ["Documents requis :",
                 Paragraph("&bull; Passeport en cours de validité <br/>"
                           "&bull; Visa d'entrée pour le Maroc",
                           styles['petit'])],
                ["Remarques :", 
                 Paragraph(participant.remarques_transport, styles['remarque'])
                 ],
            ],
            colWidths=(5 * cm, 13.5 * cm),
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('BACKGROUND', (0, 0), (0, -1), lightgrey),
            ])
            ))     
        contenu.append(Spacer(0, 0.5 * cm))
        
        # Note de frais
        if participant.frais_autres:
            contenu.append(Paragraph("Note de frais :", styles['section']))
            contenu.append(Spacer(0, 0.25 * cm))
            contenu.append(Table(
                [
                    ["Montant :", "%.2d €" % participant.frais_autres],
                    ["Versement :",
                     participant.get_modalite_versement_frais_sejour_display()]
                ],
                colWidths=(5 * cm, 13.5 * cm),
                style=TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('BACKGROUND', (0, 0), (0, -1), lightgrey),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8),
                ])))
        contenu.append(Spacer(0, 0.5 * cm))
        # Hôtel
        if participant.hotel:
            contenu.append(Paragraph("Séjour :", styles['section']))
            contenu.append(Spacer(0, 0.25 * cm))
            contenu.append(Table(
                [
                    ["Dates du séjour :", Paragraph("du {0} au {1}".format(
                        date_format(participant.date_arrivee_hotel,
                                    'SHORT_DATE_FORMAT'),
                        date_format(participant.date_depart_hotel,
                                    'SHORT_DATE_FORMAT')),
                        styles['normal'])],
                    ["Hôtel :", Paragraph(participant.hotel.libelle,
                                            styles['bold'])],
                    ["Adresse :", Paragraph(participant.hotel.adresse,
                                             styles['petit'])],
                    ["Remarques:", Paragraph(
                        "<i>Présentez-vous à l'accueil de l'hôtel avec votre "
                        "passeport <br/>pour l'attribution de votre chambre."
                        "</i>",
                        styles['remarque'])],
                    ["", Paragraph(
                        "N.B. Prévoyez de libérer votre chambre avant midi, "
                        "le jour de votre départ.",
                        styles['remarque'])]
                ],
                colWidths=(5 * cm, 13.5 * cm),
                style=TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('BACKGROUND', (0, 0), (0, -1), lightgrey),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8),
                    ('VALIGN', (0, 0), (0, -1), 'TOP'),
                ])
            ))
        contenu.append(Spacer(0, 0.5 * cm))
        # Rendu
        frame = Frame(margin_left, margin_bottom, frame_width, frame_height)
        frame.addFromList(contenu, canvas)
        canvas.showPage()

    canvas.save()
    return output_file


class StyleSheet(StyleSheet1):
    def add_style(self, name, **options):
        """
        Ajoute un style à partir des options données avec de bonnes valeurs
        par défaut.
        """
        if 'fontName' not in options:
            options['fontName'] = 'Helvetica'
        if 'fontSize' not in options:
            options['fontSize'] = 10
        if 'leading' not in options:
            options['leading'] = options['fontSize'] * 1.2
        self.add(ParagraphStyle(name, **options))


def facture_response(inscription_ou_participant):
    filename = 'Facture - %s %s.pdf' % (inscription_ou_participant.prenom,
                                         inscription_ou_participant.nom)
    response = pdf_response(filename)

    if isinstance(inscription_ou_participant, Inscription):
        facture = facture_from_inscription(inscription_ou_participant)
    else:
        facture = facture_from_participant(inscription_ou_participant)
    return generer_factures(response, [facture])


def pdf_response(filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % \
                                      urllib.parse.quote(filename.encode('utf-8'))
    return response


Coupon = namedtuple('coupon', (
    'nom_participant',
    'noms_invites',
    'infos_depart_arrivee',
    'nb_personnes',
))


COUPON_HEIGHT = 8 * cm
COUPON_SPACING = 0.5 * cm
COUPON_MARGIN_SIDE = 1 * cm


def calc_coupon_y(arrivee_depart):
    page_width, page_height = PAGESIZE
    margin_top = 1 * cm
    coupon_y = page_height - margin_top - COUPON_HEIGHT
    if arrivee_depart == 'depart':
        coupon_y -= COUPON_HEIGHT + COUPON_SPACING
    return coupon_y


# noinspection PyListCreation
def draw_coupon(canvas, styles, nom_participant, noms_invites,
                date_vol, aeroport, arrivee_depart, nb_personnes):
    page_width, page_height = PAGESIZE
    margin_left = margin_right = COUPON_MARGIN_SIDE
    coupon_width = page_width - margin_left - margin_right
    coupon_y = calc_coupon_y(arrivee_depart)
    canvas.rect(margin_left, coupon_y, coupon_width, COUPON_HEIGHT)
    padding = 0.1 * cm
    logo_x = margin_left + padding
    frame_y = coupon_y + padding
    frame_height = COUPON_HEIGHT
    logo_y = frame_y + padding
    logo_height = frame_height - 3 * padding
    logo_width = 143 * logo_height / 300
    canvas.drawImage(
        os.path.join(APP_ROOT, 'images', 'agauflogo2017vert.jpg'),
        logo_x, logo_y, logo_width, logo_height)
    frame_width = coupon_width - padding * 2 - (logo_width + padding)
    frame_x = logo_x + logo_width + padding
    frame = Frame(frame_x, frame_y, frame_width, frame_height)
    contenu = []
    contenu.append(
        Table(
            [[[Paragraph("Coupon navette", styles['grand-bold']),
               Paragraph("Bon pour transport par autobus réservé",
                         styles['normal'])],
              Paragraph(str(nb_personnes), styles['gros-numero'])]
             ],
            colWidths=[frame_width - 1.2 * cm, 1.2 * cm],
            style=TableStyle(
                  [('BACKGROUND', (0, 0), (-1, -1), lightgrey),
                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                   ('VALIGN', (0, 0), (-1, -1), 'TOP')]
              ))
    )
    hotel = "MOGADOR AGDAL 2"
    if arrivee_depart == "arrivee":
        trajet = [aeroport, hotel]
        presenter = "Veuillez présenter ce coupon au point de " \
                    "rencontre aux couleurs de l'AUF à la sortie de " \
                    "l'aéroport."
    else:
        trajet = [hotel, aeroport]
        presenter = "Veuillez présenter ce coupon au conducteur de la navette."
    contenu.append(Paragraph(trajet[0] + "&nbsp;&nbsp;→&nbsp;&nbsp;" + trajet[1],
                             styles['grand-bold']))
    contenu.append(Spacer(1, COUPON_SPACING))
    contenu.append(
        Table([[Paragraph(date_format(date_vol),
                          styles['normal']),
                Paragraph("<br/> + ".join([nom_participant] + noms_invites),
                          styles['grand'])]],
              colWidths=[2.5 * cm, frame_width - 2.5 * cm],
              style=TableStyle(
                  [('BACKGROUND', (0, 0), (0, 0), lightgrey),
                   ('FONTSIZE', (0, 0), (-1, -1), 18),
                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
              ))

    )
    contenu.append(Spacer(3, COUPON_SPACING))
    contenu.append(Paragraph(presenter, styles['petit']))
    frame.addFromList(contenu, canvas)
    notice_y = coupon_y + 0.1 * cm
    canvas.setFont('Helvetica', 10)
    canvas.drawString(frame_x, notice_y, "© AUF 2017")
    canvas.drawRightString(frame_x + frame_width, notice_y,
                           "Ce bon n'est pas transférable ni monnayable.")


def generer_coupons(output_file, coupon):
    """

    :param output_file: File
    :param coupon: Coupon
    :return:
    """
    # Styles
    styles = StyleSheet()
    styles.add_style('normal', fontName='Helvetica', fontSize=14)
    styles.add_style('normal-centered', fontName='Helvetica', fontSize=14,
                     alignment=TA_CENTER)
    styles.add_style('normal-bold', fontName='Helvetica-bold', fontSize=14)
    styles.add_style('grand', fontName='Helvetica', fontSize=18)
    styles.add_style('grand-bold', fontName='Helvetica-bold', fontSize=18)
    styles.add_style('petit', fontName='Helvetica', fontSize=12)
    styles.add_style('petit-bold', fontName='Helvetica-bold', fontSize=12)
    styles.add_style('titre', fontName='Helvetica-Bold', fontSize=15)
    styles.add_style('centered', alignment=TA_CENTER)
    styles.add_style('remarque', fontName='Helvetica-Oblique', fontSize=11)
    styles.add_style('gros-numero', fontName='Helvetica-Bold', fontSize=36)
    styles.add_style('right-aligned', alignment=TA_RIGHT)
    canvas = Canvas(output_file, pagesize=PAGESIZE)
    draw_coupon(canvas, styles, coupon.nom_participant, coupon.noms_invites,
                coupon.infos_depart_arrivee.depart_date,
                coupon.infos_depart_arrivee.depart_de,
                'depart', coupon.nb_personnes)
    draw_coupon(canvas, styles, coupon.nom_participant, coupon.noms_invites,
                coupon.infos_depart_arrivee.arrivee_date,
                coupon.infos_depart_arrivee.arrivee_a,
                'arrivee', coupon.nb_personnes)
    
    page_width, page_height = PAGESIZE
    frame_height = 10 * cm
    frame = Frame(COUPON_MARGIN_SIDE, calc_coupon_y('depart') - frame_height,
                  page_width - COUPON_MARGIN_SIDE * 2, frame_height)
    frame.addFromList([Paragraph("""<br/><br/><u>Veuillez noter que les transferts en 
    navette ne s'effectuent que dans les conditions suivantes:</u><br/><br/>     
        À votre arrivée, les transferts en navette organisés des aéroports de 
        Casablanca et de Marrakech sont uniquement à destination du lieu de 
        l’Assemblée générale, le Palais des Congrès de l'hôtel Mogador Agdal 2.
        <br/><b>Ces transferts ne sont disponibles que du 6 au 10 mai 2017.</b>
        <br/><br/>
        À votre départ, les transferts en navette oganisés à destination des 
        aéroports de Casablanca et de Marrakech se feront au même point qu'à 
        l'arrivée à l'hôtel Mogador Agdal 2.<br/>
        <b>Ces transferts ne sont disponibles que du 12 au 15 mai 2017.</b>
        <br/><br/>
        Aucun autre arrêt n'est prévu durant ces trajets.
        Si vous ne logez pas au Mogador Agdal 2, vous devez assurer, à vos 
        frais, votre déplacement entre votre hôtel et le lieu de l’Assemblée 
        générale.
        <br/><br/>
        <b>Adresse du Mogador Agdal 2:</b> Zone Touristique Agdal, Route d'Ourika, 
        Marrakech 40000, Maroc
        <br/><br/>
        <b>En cas de problème à l'arrivée, veuillez contacter:</b> <br/>Casablanca: 
        +212 6 89 91 77 19 &nbsp; &nbsp; &nbsp; Marrakech: +212 6 89 91 77 20
    """, styles['remarque'])], canvas)
    canvas.save()


def coupon_transport_response(participant):
    """

    :param participant: Participant
    :return: HttpResponse
    """
    noms_invites = participant.get_noms_invites()
    coupon = Coupon(
        nom_participant=participant.get_nom_complet(),
        noms_invites=noms_invites,
        infos_depart_arrivee=participant.get_infos_depart_arrivee(),
        nb_personnes=1 + len(noms_invites),
    )
    filename = 'Coupon transport - {}.pdf'.format(coupon.nom_participant)
    response = pdf_response(filename)
    generer_coupons(response, coupon)
    return response


