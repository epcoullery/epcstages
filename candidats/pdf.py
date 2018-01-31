import os
import tempfile

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Preformatted, Table, TableStyle

from django.utils.text import slugify 

from stages.pdf import EpcBaseDocTemplate
from .models import (
    AES_ACCORDS_CHOICES, DIPLOMA_CHOICES, DIPLOMA_STATUS_CHOICES,
    OPTION_CHOICES, RESIDENCE_PERMITS_CHOICES,
)

style_normal = PS(name='CORPS', fontName='Helvetica', fontSize=9, alignment=TA_LEFT)
style_normal_bold = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=9, alignment=TA_LEFT, spaceBefore=0.5 * cm)


class InscriptionSummaryPDF(EpcBaseDocTemplate):
    """
    PDF for summary of inscription
    """
    def __init__(self, candidate, **kwargs):
        filename = slugify('{0}_{1}'.format(candidate.last_name, candidate.first_name)) + '.pdf'
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(path, title="Dossier d'inscription", **kwargs)
        self.setNormalTemplatePage()

    def produce(self, candidate):
        # personal data
        options = dict(OPTION_CHOICES)
        diploma = dict(DIPLOMA_CHOICES)
        diploma_status = dict(DIPLOMA_STATUS_CHOICES)
        aes_accords = dict(AES_ACCORDS_CHOICES)
        residence_permits = dict(RESIDENCE_PERMITS_CHOICES)

        myTableStyle = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('SIZE', (0, 0), (-1, -1), 8)
        ])

        self.story.append(Paragraph("Données personnelles", style_normal_bold))
        data = [
            ['Nom: ', candidate.last_name, 'Date de naissance:', candidate.birth_date],
            ['Prénom:', candidate.first_name, 'Canton:', candidate.district],
            ['N° de tél.:', candidate.mobile, '', ''],
        ]
        t = Table(data, colWidths=[2 * cm, 6 * cm, 4 * cm, 5 * cm], hAlign=TA_LEFT)
        t.setStyle(myTableStyle)
        self.story.append(t)

        # Chosen Option
        data = []
        self.story.append(Paragraph("Option choisie", style_normal_bold))
        data.append([options.get(candidate.option, '')])
        t = Table(data, colWidths=[17 * cm], hAlign=TA_LEFT)
        t.setStyle(myTableStyle)
        self.story.append(t)

        # Diploma
        data = []
        self.story.append(Paragraph("Titres / diplômes /attest. prof.", style_normal_bold))
        data.append([
            diploma[candidate.diploma],
            '{0} {1}'.format(candidate.diploma_detail, diploma_status[candidate.diploma_status])
        ])

        if candidate.diploma == 1:  # CFC ASE
            data.append(['Evaluation du dernier stage', candidate.get_ok('work_certificate')])
        elif candidate.diploma == 2:  # CFC autre domaine
            data.append(['Attestation de 800h. min. domaine Enfance', candidate.get_ok('certif_of_800_childhood')])
            data.append(["Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')])
        elif candidate.diploma == 3 or candidate.diploma == 4:  # Matu. aca ou ECG ou Portfolio
            data.append(['Attestation de 800h. min. domaine Général', candidate.get_ok('certif_800_general')])
            data.append(['Attestation de 800h. min. domaine Enfance', candidate.get_ok('certif_of_800_childhood')])
            data.append(["Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')])

        if candidate.option != 'PS':
            data.append(["Contrat de travail", candidate.get_ok('contract')])
            data.append(["Promesse d'engagement", candidate.get_ok('promise')])
            data.append(["Taux d'activité", candidate.activity_rate])
        t = Table(data, colWidths=[12 * cm, 5 * cm], hAlign=TA_LEFT)
        t.setStyle(myTableStyle)
        self.story.append(t)

        # Others documents
        data = []
        self.story.append(Paragraph("Autres documents", style_normal_bold))
        docs = [
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'has_photo',
            'reflexive_text', 'marks_certificate', 'aes_accords', 'residence_permits'
        ]
        for doc in docs:
            data.append([candidate._meta.get_field(doc).verbose_name, candidate.get_ok(doc)])
        data.append(['Validation des accords AES', aes_accords[candidate.aes_accords]])
        data.append(['Autorisation de séjour (pour les personnes étrangères)', residence_permits[candidate.residence_permits]])

        t = Table(data, colWidths=[12 * cm, 5 * cm], hAlign=TA_LEFT)
        t.setStyle(myTableStyle)
        self.story.append(t)

        # Remarks
        data = []
        self.story.append(Paragraph("Remarques", style_normal_bold))
        data.append([Preformatted(candidate.comment, style_normal, maxLineLength=100)])
        t = Table(data, colWidths=[17 * cm], hAlign=TA_LEFT)
        t.setStyle(myTableStyle)
        self.story.append(t)
        self.build(self.story)
