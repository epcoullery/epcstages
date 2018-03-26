import os
import tempfile
from datetime import date
import locale

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.utils.text import slugify

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import (
    Frame, Image, NextPageTemplate, PageBreak, PageTemplate, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

locale.setlocale(locale.LC_TIME, '')

style_normal = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_LEFT)
style_bold = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=10, alignment=TA_LEFT)
style_title = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT, spaceBefore=1*cm)
style_adress = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_LEFT, leftIndent=280)
style_normal_right = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_RIGHT)
style_bold_center = PS(name="CORPS", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER)
style_footer = PS(name='CORPS', fontName='Helvetica', fontSize=7, alignment=TA_CENTER)

LOGO_EPC = find('img/logo_EPC.png')
LOGO_ESNE = find('img/logo_ESNE.png')


class EpcBaseDocTemplate(SimpleDocTemplate):
    filiere = 'Formation EDE'

    def __init__(self, filename, title='', pagesize=A4):
        super().__init__(
            filename, pagesize=pagesize, _pageBreakQuick=0,
            lefMargin=1.5 * cm, bottomMargin=1.5 * cm, topMargin=1.5 * cm, rightMargin=2.5 * cm
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

    def set_normal_template_page(self):
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


class EpcBaseLetterTemplate(EpcBaseDocTemplate):
    def __init__(self, filename, title=''):
        super().__init__(filename)
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
        # Footer
        canvas.line(doc.leftMargin, 1 * cm, doc.width + doc.leftMargin, 1 * cm)
        footer = Paragraph('Ecole Santé-social Pierre-Coullery | Prévoyance 82 - 2300 La Chaux-de-Fonds | '
                           '032 886 33 00 | cifom-epc@rpn.ch', style_footer)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        canvas.restoreState()


class ChargeSheetPDF(SimpleDocTemplate):
    """
    Génération des feuilles de charges en pdf.
    """

    def __init__(self, teacher):
        self.teacher = teacher
        filename = slugify('{0}_{1}'.format(teacher.last_name, teacher.first_name)) + '.pdf'
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(path, pagesize=A4, topMargin=0*cm, leftMargin=2*cm)
        self.story = []

    def produce(self, activities):
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
        t.setStyle(TableStyle([('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                               ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                               ('LINEABOVE', (0, -3), (-1, -1), 0.5, colors.black),
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


class ExpertEDEPDF(EpcBaseLetterTemplate):
    """
    PDF letter to expert EDE
    """

    def __init__(self, student, **kwargs):
        filename = slugify('{0}_{1}'.format(student.last_name, student.first_name)) + '.pdf'
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(path, title="", **kwargs)
        self.set_normal_template_page()

    def produce(self, student):
        # Expert adresse
        self.story.append(Paragraph(student.expert.title, style_adress))
        self.story.append(Paragraph(student.expert.full_name, style_adress))
        self.story.append(Paragraph(student.expert.street, style_adress))
        self.story.append((Paragraph(student.expert.pcode_city, style_adress)))
        ptext = """
                <br/><br/><br/>
                La Chaux-de-Fonds, le {current_date}<br/>
                N/réf.:ASH/val<br/>
                <br/><br/><br/>
                <strong>Travail de diplôme</strong>
                <br/><br/><br/>
                {expert_title},<br/><br/>
                Vous avez accepté de fonctionner comme expert{expert_accord} pour un travail de diplôme de l'un-e de nos 
                étudiant-e-s. Nous vous remercions très chaleureusement de votre disponibilité.<br/><br/>
                En annexe, nous avons l'avantage de vous remettre le travail de {student_civility_full_name},
                ainsi que la grille d'évaluation commune aux deux membres du jury.<br/><br/>
                La soutenance de ce travail de diplôme se déroulera le:<br/><br/>
                """
        self.story.append(Paragraph(ptext.format(current_date=date.today().strftime('%d %B %Y'),
                                                 expert_title=student.expert.title,
                                                 expert_accord=student.expert.adjective_endings,
                                                 student_civility_full_name=student.civility_full_name)))
        ptext = "<br/>{0} à l'Ecole Santé-social Pierre-Coullery, salle {1}<br/><br/>"
        self.story.append(Paragraph(ptext.format(student.date_exam.strftime('%A %d %B %Y à %Hh%M'),
                                                 student.room), style_bold_center))

        ptext = """
                <br/>
                L'autre membre du jury sera {internal_expert_civility} {internal_expert_full_name}, {internal_expert_role} dans notre école.<br/>
                <br/>
                Par ailleurs, nous nous permettons de vous faire parvenir en annexe le formulaire "Indemnisation d'experts aux examens"
                que vous voudrez bien compléter au niveau des "données privées / coordonnées de paiement" et nous retourner dans les meilleurs délais.
                <br/><br/>
                Restant à votre disposition pour tout complément d'information et en vous remerciant de
                l'attention que vous porterez à la présente, nous vous prions d'agréer, {expert_title}, l'asurance de notre considération distinguée.<br/>
                <br/><br/><br/>
                La responsable de filière:<br/>
                <br/><br/>
                Ann Schaub-Murray
                <br/><br/><br/>
                Annexes: ment.
                <br/><br/>
                Copies pour information: <br/>
                - {student_civility} {student_full_name}, {student_role} <br/>
                - {internal_expert_civility2} {internal_expert_full_name2}, {internal_expert_role2}
                """
        self.story.append(Paragraph(ptext.format(internal_expert_civility=student.internal_expert.civility,
                                                 internal_expert_full_name=student.internal_expert.full_name,
                                                 internal_expert_role=student.internal_expert.role,
                                                 expert_title=student.expert.title,
                                                 student_civility=student.civility,
                                                 student_full_name=student.full_name,
                                                 student_role=student.role,
                                                 internal_expert_civility2=student.internal_expert.civility,
                                                 internal_expert_full_name2=student.internal_expert.full_name,
                                                 internal_expert_role2=student.internal_expert.role), style_normal))
        self.build(self.story)
