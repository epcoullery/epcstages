import os
import tempfile
from datetime import date

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.utils.text import slugify
from django.utils.dateformat import format as django_format
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import (
    Frame, Image, NextPageTemplate, PageBreak, PageTemplate, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

style_normal = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment = TA_LEFT)
style_bold = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=10, alignment = TA_LEFT)
style_title = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=12, alignment = TA_LEFT, spaceBefore=1*cm)
style_adress = PS(name='CORPS', fontName='Helvetica', fontSize=10, alignment = TA_LEFT, leftIndent=280)
style_normal_right = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment = TA_RIGHT)
style_normal_title = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=9, alignment = TA_LEFT, spaceBefore=0.7*cm)

LOGO_EPC = find('img/logo_EPC.png')
LOGO_ESNE = find('img/logo_ESNE.png')


class EpcBaseDocTemplate(SimpleDocTemplate):
    filiere = 'Formation EDE'

    def __init__(self, filename, title='', pagesize=A4):
        super().__init__(
            filename, pagesize=pagesize, _pageBreakQuick=0,
            lefMargin=1.5 * cm, bottomMargin=1.5 * cm, topMargin=1.5 * cm, rightMargin=1.5 * cm
        )
        self.story = []
        self.title = title

    def header(self, canvas, doc):
        canvas.saveState()
        canvas.drawImage(
            LOGO_EPC, doc.leftMargin, doc.height - 0.5 * cm, 5 * cm, 3 * cm, preserveAspectRatio=True
        )
        canvas.drawImage(
            LOGO_ESNE, doc.width - 2 * cm, doc.height - 0.5 * cm, 5 * cm, 3 * cm, preserveAspectRatio=True
        )
        canvas.line(doc.leftMargin, doc.height - 0.5 * cm, doc.width + doc.leftMargin, doc.height - 0.5 * cm)
        canvas.drawString(doc.leftMargin, doc.height - 1.1 * cm, self.filiere)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height - 1.1 * cm, self.title)
        canvas.line(doc.leftMargin, doc.height - 1.3 * cm, doc.width + doc.leftMargin, doc.height - 1.3 * cm)
        canvas.restoreState()

    def later_header(self, canvas, doc):
        canvas.saveState()
        canvas.line(doc.leftMargin, doc.height + 1 * cm, doc.width + doc.leftMargin, doc.height + 1 * cm)
        canvas.drawString(doc.leftMargin, doc.height + 0.5 * cm, self.filiere)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height + 0.5 * cm, self.title)
        canvas.line(doc.leftMargin, doc.height + 0.2 * cm, doc.width + doc.leftMargin, doc.height + 0.2 * cm)
        canvas.restoreState()

    def setNormalTemplatePage(self):
        first_page_table_frame = Frame(
            self.leftMargin, self.bottomMargin, self.width + 1 * cm, self.height - 4 * cm,
            id='first_table', showBoundary=0, leftPadding=0 * cm
        )
        later_pages_table_frame = Frame(
            self.leftMargin, self.bottomMargin, self.width + 1 * cm, self.height - 2 * cm,
            id='later_table', showBoundary=0, leftPadding=0 * cm
        )
        # Page template
        first_page = PageTemplate(id='FirstPage', frames=[first_page_table_frame], onPage=self.header)
        later_pages = PageTemplate(id='LaterPages', frames=[later_pages_table_frame], onPage=self.later_header)
        self.addPageTemplates([first_page, later_pages])
        self.story = [NextPageTemplate(['*', 'LaterPages'])]


class ChargeSheetPDF(SimpleDocTemplate):
    """
    Génération des feuilles de charges en pdf.
    """

    def __init__(self, teacher):
        self.teacher = teacher
        filename = slugify('{0}_{1}'.format(teacher.last_name, teacher.first_name)) + '.pdf'
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(path, pagesize=A4, topMargin=0*cm, leftMargin=2*cm)

    def produce(self, activities):
        self.story = []
        header = open(find('img/header.gif'), 'rb')
        self.story.append(Image(header, width=520, height=75))
        self.story.append(Spacer(0, 2*cm))
        destinataire = '{0}<br/>{1}'.format(self.teacher.civility, str(self.teacher))
        self.story.append(Paragraph(destinataire, style_adress))
        self.story.append(Spacer(0, 2*cm))

        data = [[settings.CHARGE_SHEET_TITLE]]

        data.append(["Report de l'année précédente", '{0:3d} pér.'.format(self.teacher.previous_report)])
        data.append(['Mandats', '{0:3d} pér.'.format(activities['tot_mandats'])])

        for act in activities['mandats']:
            data.append(['    * {0} ({1} pér.)'.format(act.subject, act.period)])

        data.append(['Enseignement (coef.2)', '{0:3d} pér.'.format(activities['tot_ens'])])
        data.append(['Formation continue et autres tâches', '{0:3d} pér.'.format(activities['tot_formation'])])
        data.append(['Total des heures travaillées', '{0:3d} pér.'.format(activities['tot_trav']),
                     '{0:4.1f} %'.format(activities['tot_trav']/21.50)])
        data.append(['Total des heures payées', '{0:3d} pér.'.format(activities['tot_paye']),
                     '{0:4.1f} %'.format(activities['tot_paye']/21.50)])
        data.append(["Report à l'année prochaine", '{0:3d} pér.'.format(activities['report'])])

        t = Table(data, colWidths=[12*cm, 2*cm, 2*cm])
        t.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEABOVE', (0, -3) ,(-1, -1), 0.5, colors.black),
            ('FONT', (0, -2), (-1, -2), 'Helvetica-Bold'),
        ]))
        t.hAlign = TA_CENTER
        self.story.append(t)
        self.story.append(Spacer(0, 2*cm))
        d = 'La Chaux-de-Fonds, le {0}'.format(date.today().strftime('%d.%m.%y'))
        self.story.append(Paragraph(d, style_normal))
        self.story.append(Spacer(0, 0.5*cm))
        self.story.append(Paragraph('la direction', style_normal))
        max_total = settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION
        if activities['tot_paye'] == max_total and activities['tot_paye'] != activities['tot_trav']:
             self.story.append(Spacer(0, 1 * cm))
             d = 'Je soussigné-e déclare accepter les conditions ci-dessus pour la régularisation de mon salaire.'
             self.story.append(Paragraph(d, style_normal))
             self.story.append(Spacer(0, 1 * cm))
             d = 'Lieu, date et signature: ___________________________________________________________________________'
             self.story.append(Paragraph(d, style_normal))
        self.story.append(PageBreak())
        self.build(self.story)
        header.close()


class UpdateDataFormPDF(SimpleDocTemplate):
    """
    Génération des formulaires PDF de mise à jour des données.
    """
    def __init__(self, path):
        super().__init__(path, pagesize=A4, topMargin=0*cm, leftMargin=2*cm)
        self.text = (
            "Afin de mettre à jour nos bases de données, nous vous serions reconnaissant "
            "de contrôler les données ci-dessous qui vous concernent selon votre filière "
            "et de retourner le présent document corrigé et complété à votre maître de classe jusqu'au "
            "vendredi 9 septembre prochain.<br/><br/>"
            "Nous vous remercions de votre précieuse collaboration.<br/><br/>"
            "Le secrétariat"
        )
        self.underline = '__________________________________'

    def produce(self, klass):
        self.story = []
        header = open(find('img/header.gif'), 'rb')
        for student in klass.student_set.filter(archived=False):
            self.story.append(Image(header, width=520, height=75))
            self.story.append(Spacer(0, 2*cm))
            destinataire = '{0}<br/>{1}<br/>{2}'.format(student.civility, student.full_name, student.klass)
            self.story.append(Paragraph(destinataire, style_adress))
            self.story.append(Spacer(0, 2*cm))
            self.story.append(Paragraph('{0},<br/>'.format(student.civility), style_normal))
            self.story.append(Paragraph(self.text, style_normal))
            self.story.append(Spacer(0, 2*cm))

            data = [['Données enregistrées', 'Données corrigées et/ou complétées']]
            t = Table(data, colWidths=[8*cm, 8*cm])
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ]))
            t.hAlign = TA_CENTER
            self.story.append(t)

            # Personal data
            data = [
                ['NOM', student.last_name, self.underline],
                ['PRENOM', student.first_name, self.underline],
                ['ADRESSE', student.street, self.underline],
                ['LOCALITE', student.pcode_city, self.underline],
                ['MOBILE', student.mobile, self.underline],
                ['CLASSE', student.klass, self.underline],
                ['', '', ''],
            ]

            # Corporation data
            if self.is_corp_required(student.klass.name):
                if student.corporation is None:
                    data.extend([
                        ["Données de l'Employeur", '', ''],
                        ['NOM', '', self.underline],
                        ['ADRESSE', '', self.underline],
                        ['LOCALITE', '', self.underline],
                        ['', '', '']
                    ])
                else:
                    data.extend([
                        ["Données de l'Employeur", '', ''],
                        ['NOM', student.corporation.name, self.underline],
                        ['ADRESSE', student.corporation.street, self.underline],
                        ['LOCALITE', student.corporation.pcode_city, self.underline],
                        ['', '', '']
                    ])

            # Instructor data
            if self.is_instr_required(student.klass.name):
                if student.instructor is None:
                    data.extend([
                        ['Données du FEE/FPP (personne de contact pour les informations)', '', ''],
                        ['NOM', '', self.underline],
                        ['PRENOM', '', self.underline],
                        ['TELEPHONE', '', self.underline],
                        ['E-MAIL', '', self.underline],
                    ])
                else:
                    data.extend([
                        ['Données du FEE/FPP (personne de contact pour les informations)', '', ''],
                        ['NOM', student.instructor.last_name, self.underline],
                        ['PRENOM', student.instructor.first_name, self.underline],
                        ['TELEPHONE', student.instructor.tel, self.underline],
                        ['E-MAIL', student.instructor.email, self.underline],
                    ])

            t = Table(data, colWidths=[3*cm, 5*cm, 8*cm])
            t.setStyle(TableStyle([
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ]))
            t.hAlign = TA_CENTER
            self.story.append(t)
            self.story.append(PageBreak())
        if len(self.story) == 0:
            self.story.append(Paragraph("Pas d'élèves dans cette classe", style_normal))

        self.build(self.story)
        header.close()

    def is_corp_required(self, klass_name):
        return any(el in klass_name for el in ['FE', 'EDS', 'EDEpe'])

    def is_instr_required(self, klass_name):
        return any(el in klass_name for el in ['FE', 'EDS'])


class InscriptionSummaryPDF(EpcBaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, "Dossier d'inscription")
        self.setNormalTemplatePage()

    def produce(self, candidate):
        ts = TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 0), (0, -1), 'Helvetica'),
            ('SIZE', (0, 0), (0, -1), 9),
        ])

        # Personal data
        data = []
        self.story.append(Paragraph('Données personnelles', style_normal_title))
        data.extend([
            ['Nom: ', candidate.last_name, 'Date de naissance: ', django_format(candidate.birth_date, "j F Y ")],
            ['Prénom: ', candidate.first_name, 'Canton: ', candidate.district],
            ['No de tél.: ', candidate.mobile]
        ])
        t = Table(data, colWidths=[4 * cm, 5 * cm, 4 * cm, 4 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Inscription
        data = []
        self.story.append(Paragraph("Inscription", style_normal_title))
        data.extend([
            [candidate.get_section_display(), candidate.get_option_display()]
        ])
        t = Table(data, colWidths=[6 * cm, 11 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Diploma
        data = []
        self.story.append(Paragraph("Titres / diplôme / Attestations", style_normal_title))
        detail = '' if candidate.diploma_detail == '' else '({0})'.format(candidate.diploma_detail)
        data.extend([
            ['{0} {1}'.format(candidate.get_diploma_display(),detail), 'statut: {0}'.format(candidate.get_diploma_status_display())]
        ])

        if candidate.diploma == 1:  #CFC ASE
            data.extend([
                ['Evaluation du dernier stage ASE et/ou dernier rapport de formation', candidate.get_ok('work_certificate')]
            ])
        if candidate.diploma == 2:  # CFC autre domaine
            data.extend([
                ["Attestation de 800h. dans un seul lieu d'accueil de l'enfance", candidate.get_ok('certif_of_800_childhood')],
                ["Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')]
            ])

        if candidate.diploma == 3:  # Matur, Ecole cult. générale
            data.extend([
                ["Certif. de travail/stage de 800h. dans n'importe quel domaine", candidate.get_ok('certif_of_800_general')],
                ["Attestation de 800h. dans un seul lieu d'accueil de l'enfance", candidate.get_ok('certif_of_800_childhood')],
                ["Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')]
            ])

        if candidate.diploma == 4:  # Protfolio
            data.extend([
                ["Certif. de travail/stage de 800h. dans n'importe quel domaine", candidate.get_ok('certif_of_800_general')],
                ["Attestation de 800h. dans un seul lieu d'accueil de l'enfance", candidate.get_ok('certif_of_800_childhood')],
                ["Bilan de l'activité professionnelle", candidate.get_ok('work_certificate')]
            ])
        t = Table(data, colWidths=[13 * cm, 4*cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Others documents
        data = []
        self.story.append(Paragraph("Autres documents", style_normal_title))
        docs_required = [
            'registration_form', 'certificate_of_payement', 'police_record', 'cv', 'has_photo', 'reflexive_text',
            'marks_certificate', 'handicap'
        ]
        data.extend([[candidate._meta.get_field(doc).verbose_name, candidate.get_ok(doc)] for doc in docs_required])
        t = Table(data, colWidths=[13 * cm, 4 * cm], hAlign=TA_LEFT)
        t.setStyle(ts)
        self.story.append(t)

        # Remarks
        self.story.append(Paragraph("Remarques", style_normal_title))
        self.story.append(Paragraph(candidate.comment, style_normal))
        self.build(self.story)