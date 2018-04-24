from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm
from reportlab.platypus import PageTemplate, Paragraph, Spacer, Table, TableStyle

from django.utils.dateformat import format as django_format
from django.utils.text import slugify 

from stages.pdf import EpcBaseDocTemplate, LOGO_EPC, LOGO_ESNE, style_normal, style_bold
from .models import (
    AES_ACCORDS_CHOICES, DIPLOMA_CHOICES, DIPLOMA_STATUS_CHOICES,
    OPTION_CHOICES, RESIDENCE_PERMITS_CHOICES,
)


class InscriptionSummaryPDF(EpcBaseDocTemplate):
    """
    PDF for summary of inscription
    """
    def __init__(self, candidate, **kwargs):
        filename = slugify('{0}_{1}'.format(candidate.last_name, candidate.first_name)) + '.pdf'
        super().__init__(filename, **kwargs)
        self.addPageTemplates([
            PageTemplate(id='FirstPage', frames=[self.page_frame], onPage=self.header)
        ])

    def header(self, canvas, doc):
        section = "Filière EDE"
        title = "Dossier d'inscription"

        canvas.saveState()
        canvas.drawImage(
            LOGO_EPC, doc.leftMargin, doc.height - 1.5 * cm, 5 * cm, 3 * cm, preserveAspectRatio=True
        )
        canvas.drawImage(
            LOGO_ESNE, doc.width - 2.5 * cm, doc.height - 1.2 * cm, 5 * cm, 3.3 * cm, preserveAspectRatio=True
        )
        canvas.line(doc.leftMargin, doc.height - 2 * cm, doc.width + doc.leftMargin, doc.height - 2 * cm)
        canvas.drawString(doc.leftMargin, doc.height - 2.5 * cm, section)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height - 2.5 * cm, title)
        canvas.line(doc.leftMargin, doc.height - 2.7 * cm, doc.width + doc.leftMargin, doc.height - 2.7 * cm)
        canvas.restoreState()

    def produce(self, candidate):
        # personal data
        options = dict(OPTION_CHOICES)
        diploma = dict(DIPLOMA_CHOICES)
        diploma_status = dict(DIPLOMA_STATUS_CHOICES)
        aes_accords = dict(AES_ACCORDS_CHOICES)
        residence_permits = dict(RESIDENCE_PERMITS_CHOICES)

        ts = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ])

        # Personal data
        self.story.append(Spacer(0, 2 * cm))
        self.story.append(Paragraph("Données personnelles", style_bold))
        data = [
            ['Nom: ', candidate.last_name,
             'Date de naissance:',
             django_format(candidate.birth_date, 'j F Y') if candidate.birth_date else '?'],
            ['Prénom:', candidate.first_name, 'Canton:', candidate.district],
            ['N° de tél.:', candidate.mobile, '',''],
        ]
        t = Table(data, colWidths=[4 * cm, 5 * cm, 4 * cm, 4 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Inscription
        self.story.append(Paragraph("Option choisie", style_bold))
        data = [
            [candidate.get_section_display(), candidate.get_option_display()]
        ]
        t = Table(data, colWidths=[6 * cm, 11 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Diploma
        self.story.append(Paragraph("Titres / diplôme / Attestations", style_bold))
        detail = '({0})'.format(candidate.diploma_detail) if candidate.diploma_detail else ''
        data = [
            ['{0} {1}'.format(candidate.get_diploma_display(), detail),
             'statut: {0}'.format(candidate.get_diploma_status_display())]
        ]

        if candidate.diploma == 1:  # CFC ASE
            data.append([
                'Evaluation du dernier stage ASE et/ou dernier rapport de formation',
                candidate.get_ok('work_certificate'),
            ])

        elif candidate.diploma == 2:  # CFC autre domaine
            data.append([
                "Attestation de 800h. dans un seul lieu d'accueil de l'enfance",
                candidate.get_ok('certif_of_800_childhood')
            ])
            data.append([
                "Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')
            ])

        elif candidate.diploma == 3:  # Matur, Ecole cult. générale
            data.extend([
                ["Certif. de travail/stage de 800h. dans n'importe quel domaine",
                 candidate.get_ok('certif_of_800_general')],
                ["Attestation de 800h. dans un seul lieu d'accueil de l'enfance",
                 candidate.get_ok('certif_of_800_childhood')],
                ["Bilan de l'activité professionnelle",
                 candidate.get_ok('work_certificate')],
            ])

        elif candidate.diploma == 4:  # Portfolio
            data.extend([
                ["Certif. de travail/stage de 800h. dans n'importe quel domaine",
                 candidate.get_ok('certif_of_800_general')],
                ["Attestation de 800h. dans un seul lieu d'accueil de l'enfance",
                 candidate.get_ok('certif_of_800_childhood')],
                ["Bilan de l'activité professionnelle",
                 candidate.get_ok('work_certificate')],
            ])

        if candidate.option != 'PS':
            data.append(["Contrat de travail", candidate.get_ok('contract')])
            data.append(["Promesse d'engagement", candidate.get_ok('promise')])
            data.append(["Taux d'activité", candidate.activity_rate])
        t = Table(data, colWidths=[13 * cm, 4 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Other documents
        self.story.append(Paragraph("Autres documents", style_bold))
        data = []
        docs_required = [
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'has_photo',
            'reflexive_text', 'marks_certificate', 'handicap',
        ]
        for doc in docs_required:
            data.append([candidate._meta.get_field(doc).verbose_name, candidate.get_ok(doc)])
        data.append(['Validation des accords AES', aes_accords[candidate.aes_accords]])
        data.append(['Autorisation de séjour (pour les personnes étrangères)', residence_permits[candidate.residence_permits]])

        t = Table(data, colWidths=[13 * cm, 4 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Remarks
        self.story.append(Paragraph("Remarques", style_bold))
        self.story.append(Paragraph(candidate.comment, style_normal))

        self.build(self.story)
