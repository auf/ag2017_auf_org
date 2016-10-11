# encoding: utf-8

import os
from datetime import date

from django.utils.formats import number_format, date_format
from django.utils.dateformat import time_format
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.colors import black, lightgrey
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.units import cm

from ag.gestion import APP_ROOT


PAGESIZE = letter


# noinspection PyTypeChecker
def generer_factures(output_file, participants):

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

    canvas = Canvas(output_file, pagesize=PAGESIZE)
    for participant in participants:

        # Préparation de certaines chaînes
        nom_participant = ' '.join((
            participant.get_genre_display(), participant.prenom,
            participant.nom
        ))
        numero_facture = u"000A09-%02d" % participant.numero_facture
        date_facturation = date_format(participant.date_facturation,
                                       'SHORT_DATE_FORMAT')
        adresse = participant.get_adresse_facturation()

        # Logos
        logo_height = 52
        logo_width = 130 * logo_height / 91
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'logoaufnb.jpg'),
            margin_left, page_height - margin_top - logo_height,
            logo_width, logo_height
        )
        logo_width = 195 * logo_height / 90
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'logoagN.jpg'),
            page_width - margin_right - logo_width,
            page_height - margin_top - logo_height,
            logo_width, logo_height
        )

        # Adresse de l'AUF
        x = margin_left + 75
        y = page_height - margin_top - 8
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(x, y, u"Agence universitaire de la Francophonie")
        y -= 12
        canvas.setFont('Helvetica', 8)
        for s in [
            u"Secrétariat de l'assemblée générale",
            u"Case postale du Musée C.P. 49714",
            u"Montréal (Québec), H3T 2A5, Canada",
            u"Courriel : ag2013@auf.org  Site : www.ag2013.auf.org",
        ]:
            canvas.drawString(x, y, s)
            y -= 10

        # Titre
        y -= 2 * cm
        x = margin_left
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(x, y, u"Reçu de paiement")

        # Adresse
        y -= 1.5 * cm
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(x, y - 10, u"Pour:")

        x += 1.5 * cm
        canvas.setFont('Helvetica', 10)
        p = Paragraph(u'<br/>'.join([
            nom_participant,
            adresse['adresse'],
            adresse['ville'],
            adresse['code_postal'],
            adresse['pays']
        ]), styles['normal'])
        w, h = p.wrap(8 * cm, 5 * cm)
        p.drawOn(canvas, x, y - h)

        # Autres infos
        x += 8 * cm
        t = Table(
            [
                [u"Date d'émission", date_facturation],
                [u"# Facture", numero_facture],
                [
                    u"# Dossier",
                    u"CGRM%d" % participant.etablissement.id
                    if participant.etablissement else u""
                ],
                [u"# Imputation", u"70810." + participant.imputation],
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
        y -= 6 * cm
        t = Table(
            [
                [u"Détails"],
                [
                    u"Frais de participation à la 17e assemblée générale - "
                    u"Marrakech (Maroc) - 9 au 11 mai 2017"
                ],
                [
                    u"- Frais d'inscription",
                    number_format(participant.frais_inscription_facture, 2) +
                    u" €"
                ],
                [
                    u"- Forfaits supplémentaires",
                    number_format(participant.frais_activites_facture, 2) +
                    u" €"
                ],
            ] +
            (
                [[
                    u"- Frais de supplément chambre double",
                    number_format(participant.frais_hebergement_facture, 2) +
                    u" €"
                ]]
                if participant.frais_hebergement_facture else []
            ) +
            [
                [
                    u"",
                    u"Montant total: " +
                    number_format(participant.total_facture, 2) + u" €"
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
    styles.add_style('normal', fontName='Helvetica', fontSize=8)
    styles.add_style('bold', fontName='Helvetica-bold', fontSize=8)
    styles.add_style('titre', fontName='Helvetica-Bold', fontSize=15)
    styles.add_style('sous-titre', fontName='Helvetica-Bold', fontSize=11)
    styles.add_style('right-aligned', alignment=TA_RIGHT)
    styles.add_style('section', fontName='Helvetica-Bold', fontSize=10)
    styles.add_style('itineraire-header', fontName='Helvetica-Bold', fontSize=7)
    styles.add_style('itineraire', fontSize=8)
    styles.add_style('bullet', bulletIndent=18, fontSize=8)
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
        logo_height = 52
        logo_width = 130 * logo_height / 91
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'logoaufnb.jpg'),
            margin_left, page_height - margin_top - logo_height,
            logo_width, logo_height
        )
        logo_width = 195 * logo_height / 90
        canvas.drawImage(
            os.path.join(APP_ROOT, 'images', 'logoagN.jpg'),
            page_width - margin_right - logo_width,
            page_height - margin_top - logo_height,
            logo_width, logo_height
        )

        # Adresse de l'AUF
        x = margin_left + 75
        y = page_height - margin_top - 8
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(x, y, u"Agence universitaire de la Francophonie")
        y -= 12
        canvas.setFont('Helvetica', 8)
        for s in [
            u"Secrétariat de l'assemblée générale",
            u"Case postale du Musée C.P. 49714",
            u"Montréal (Québec), H3T 2A5, Canada",
            u"Courriel : ag2013@auf.org  Site : www.ag2013.auf.org",
        ]:
            canvas.drawString(x, y, s)
            y -= 10
        contenu.append(Spacer(0, 2 * cm))

        # Titre
        contenu.append(Paragraph(
            u"Paris, le " + date_format(date.today(), 'SHORT_DATE_FORMAT'),
            styles['right-aligned']
        ))

        contenu.append(Paragraph(u"ITINÉRAIRE DE VOYAGE", styles['titre']))
        contenu.append(Paragraph(
            u"(Assemblée générale AUF 2013)", styles['sous-titre']
        ))
        contenu.append(Spacer(0, 0.25 * cm))

        # Coordonnées
        contenu.append(Table(
            [
                [u"Passager :", nom_participant],
                [u"Institution :", participant.nom_institution()],
                [u"Téléphone :", participant.telephone],
                [u"Télécopieur :", participant.telecopieur],
                [u"Courriel :", participant.courriel],
                [u"Bureau régional AUF :",
                 participant.get_nom_bureau_regional()],
            ],
            colWidths=(4 * cm, 14.5 * cm),
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ])
        ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Itinéraire
        contenu.append(Paragraph(u"Itinéraire :", styles['section']))
        contenu.append(Spacer(0, 0.25 * cm))
        contenu.append(Table(
            [[
                Paragraph(header, styles['itineraire-header'])
                for header in [
                    u"Date de départ", u"Ville de départ",
                    u"Ville d'arrivée", u"Compagnie aérienne",
                    u"Numéro de vol", u"Heure de départ",
                    u"Heure d'arrivée", u"Date d'arrivée"
                ]
            ]] +
            [
                [
                    Paragraph(s, styles['itineraire'])
                    for s in [
                        date_format(vol.date_depart, 'SHORT_DATE_FORMAT')
                        if vol.date_depart else u'',
                        vol.ville_depart,
                        vol.ville_arrivee,
                        vol.compagnie,
                        vol.numero_vol,
                        time_format(vol.heure_depart, 'H:i')
                        if vol.heure_depart else u'',
                        time_format(vol.heure_arrivee, 'H:i')
                        if vol.heure_arrivee else u'',
                        date_format(vol.date_arrivee, 'SHORT_DATE_FORMAT')
                        if vol.date_arrivee else u'',
                    ]
                ]
                for vol in vols
            ],
            colWidths=(
                2.5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2 * cm, 1.5 * cm,
                1.5 * cm, 2.5 * cm
            ),
            style=TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, black),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, black),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
            ])

        ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Retrait du billet
        contenu.append(Paragraph(u"Retrait des titres de transport:",
                                 styles['section']))

        contenu.append(Paragraph(
            participant.get_modalite_retrait_billet_display(),
            styles['normal']
        ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Documents requis
        contenu.append(Paragraph(u"Documents requis :", styles['section']))

        contenu.append(Paragraph(
            u"<bullet>&bull;</bullet>Passeport en cours de validité",
            styles['bullet']
        ))
        contenu.append(Paragraph(
            u"<bullet>&bull;</bullet>Visa de transit",
            styles['bullet']
        ))
        contenu.append(Paragraph(
            u"<bullet>&bull;</bullet>Visa d'entrée pour le Brésil",
            styles['bullet']
        ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Remarques
        if participant.remarques_transport:
            contenu.append(Paragraph(u"Remarques :", styles['section']))
            
            contenu.append(Paragraph(
                participant.remarques_transport, styles['normal']
            ))
            contenu.append(Spacer(0, 0.5 * cm))

        # Prise en charge dans ville de transit
        if participant.frais_autres:
            contenu.append(Paragraph(u"Prise en charge de votre séjour dans la "
                                     u"(les) ville(s) de transit :",
                                     styles['section']))
            contenu.append(Spacer(0, 0.25 * cm))
            contenu.append(Table([
                    [u"Montant:", u"%.2d €" % participant.frais_autres],
                    [u"Versement:",
                     participant.get_modalite_versement_frais_sejour_display()],
                ],
                colWidths=(
                    2 * cm, 8 * cm,
                    ),
                style=TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0.5, black),
                    ('LINEBELOW', (0, 0), (-1, -1), 0.5, black),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
                    ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ]),
                hAlign='LEFT',))

            contenu.append(Spacer(0, 0.5 * cm))

        # Hôtel
        if participant.hotel:
            contenu.append(Paragraph(u"Hôtel réservé:", styles['section']))

            contenu.append(Paragraph(participant.hotel.libelle, styles['bold']))
            contenu.append(Paragraph(participant.hotel.adresse,
                                     styles['normal']))
            contenu.append(Paragraph("du {0} au {1}".format(
                date_format(participant.date_arrivee_hotel,
                            'SHORT_DATE_FORMAT'),
                date_format(participant.date_depart_hotel,
                            'SHORT_DATE_FORMAT')),
                styles['bold']))

        contenu.append(Paragraph(
            u"Attention ! Veuillez tenir compte de l'heure du vol de départ de "
            u"Sao paulo dans la sélection d'une excursion libre (le cas "
            u"échéant).",
            styles['itineraire-header']
        ))
        
        contenu.append(Paragraph(
            u"N.B. Les départs de votre hotel sont prévus 4 heures avant le "
            u"décollage de votre avion.",
            styles['itineraire-header']
        ))
        contenu.append(Spacer(0, 0.5 * cm))

        # Instructions
        contenu.append(Paragraph(u"IMPORTANT", styles['important']))
        contenu.append(Spacer(0, 0.25 * cm))
        contenu.append(Paragraph(
            u"Document signé avec la mention "
            u"« bon pour accord », à retourner impérativement dans les 48 "
            u"heures suivant la réception",
            styles['bold']
        ))
        contenu.append(Spacer(0, 0.75 * cm))

        # Signature
        contenu.append(Table(
            [
                [u"Bon pour accord", u"", u"Signature obligatoire"],
                [u"", u"", u""],
            ],
            colWidths=[7 * cm, 4.5 * cm, 7 * cm],
            rowHeights=[None, 1.5 * cm],
            style=TableStyle([
                ('BOX', (0, 1), (0, 1), 0.5, black),
                ('BOX', (2, 1), (2, 1), 0.5, black),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
        ))

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
