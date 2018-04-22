import os
import tempfile
from datetime import date

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.utils.dateformat import format as django_format
from django.utils.text import slugify

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import (
    Frame, Image, NextPageTemplate, PageBreak, PageTemplate, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle, Preformatted, Flowable
)


style_normal = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_LEFT)
style_bold = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=8, spaceBefore=0.3*cm, alignment=TA_LEFT)
style_title = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT, spaceBefore=1*cm)
style_adress = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_LEFT, leftIndent=10*cm)
style_normal_right = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment=TA_RIGHT)
style_bold_center = PS(name="CORPS", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER)
style_footer = PS(name='CORPS', fontName='Helvetica', fontSize=7, alignment=TA_CENTER)
style_bold_center_12 = PS(name="CORPS", fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER)

LOGO_EPC = find('img/logo_EPC.png')
LOGO_ESNE = find('img/logo_ESNE.png')
LOGO_EPC_LONG = find('img/header.gif')

EXPERT_MANDAT = 'EXPERT'
MENTOR_MANDAT = 'MENTOR'
EXPERT_ACCOUNT = "3'000'XXXX"
MENTOR_ACCOUNT = "3'000'YYYY"
OTP_EDE_PS_OTP = "CIFO 000.000.XXXX"
OTP_EDE_PE_OTP = "CIFO 000.000.YYYY"

class MCLine(Flowable):
   """Line flowable --- draws a line in a flowable"""

   def __init__(self,width):
      Flowable.__init__(self)
      self.width = width

   def __repr__(self):
      return "Line(w=%s)" % self.width

   def draw(self):
      self.canv.line(0,0,self.width,0)


class EpcBaseDocTemplate(SimpleDocTemplate):
    points = '..............................................................................................'

    def __init__(self, filename):
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(
            path,
            pagesize=A4,
            leftMargin=2.5 * cm, bottomMargin=1 * cm, topMargin=1 * cm, rightMargin=2.5 * cm
        )
        self.page_frame = Frame(
            2.5 * cm, 1 * cm, self.width-2.5, self.height - 3 * cm,
            id='first_table', showBoundary=0, leftPadding=0 * cm
        )
        self.story = []

    def header(self, canvas, doc):
        canvas.saveState()
        canvas.drawImage(
                LOGO_EPC, doc.leftMargin, doc.height - 1.5 * cm, 5 * cm, 3 * cm, preserveAspectRatio=True
        )
        canvas.drawImage(
                LOGO_ESNE, doc.width - 2.5 * cm, doc.height - 1.2 * cm, 5 * cm, 3.3 * cm, preserveAspectRatio=True
        )

        # Footer
        canvas.line(doc.leftMargin, 1 * cm, doc.width + doc.leftMargin, 1 * cm)
        footer = Paragraph(settings.FOOTER_PAGE, style_footer)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    def header_iso(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.black)
        canvas.setFillColorRGB(0, 0, 0, 0.2)
        canvas.rect(2.5 * cm, doc.height - 0.5 * cm, doc.width, 1.5 * cm, fill=True)
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica-Bold', 11)
        canvas.drawString(2.7 * cm, doc.height + 0.5 * cm, "CIFOM")
        canvas.setFont('Helvetica', 7)
        canvas.drawString(2.7 * cm, doc.height + 0.1 * cm, "Centre interrégional de formation")
        canvas.drawString(2.7 * cm, doc.height - 0.15 * cm, "des montagnes neuchâteloises")
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(8 * cm, doc.height + 0.5 * cm, "INDEMNISATION D'EXPERTS")
        canvas.drawString(16 * cm, doc.height + 0.5 * cm, "51.05 FO 05")
        canvas.drawString(8 * cm, doc.height - 0.1 * cm, "AUX EXAMENS")
        canvas.setFont('Helvetica-Bold', 11)
        canvas.drawString(8 * cm, doc.height - 2.5 * cm, "Ecole Santé-social Pierre-Coullery")
        canvas.restoreState()

    def header_ede_summary(self, canvas, doc):
        section = "Filière EDE"
        title = "Dossier d'inscription"

        canvas.saveState()
        canvas.drawImage(LOGO_EPC, doc.leftMargin, doc.height - 1.5 * cm, 5 * cm, 3 * cm, preserveAspectRatio=True)
        canvas.drawImage(
                LOGO_ESNE, doc.width - 2.5 * cm, doc.height - 1.2 * cm, 5 * cm, 3.3 * cm, preserveAspectRatio=True
        )
        canvas.line(doc.leftMargin, doc.height - 2 * cm, doc.width + doc.leftMargin, doc.height - 2 * cm)
        canvas.drawString(doc.leftMargin, doc.height - 2.5 * cm, section)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height - 2.5 * cm, title)
        canvas.line(doc.leftMargin, doc.height - 2.7 * cm, doc.width + doc.leftMargin, doc.height - 2.7 * cm)
        canvas.restoreState()

    def _formating(self, text):
        return Preformatted(text, style_normal, maxLineLength=25)

    def add_private_data(self, person):
        self.story.append(Spacer(0, 1 * cm))
        self.story.append(Paragraph('DONNÉES PRIVÉES', style_bold))
        data = [
            [self._formating('NOM : '), person.last_name or self.points],
            [self._formating('Prénom :'), person.first_name or self.points],
            [self._formating('Date de naissance :'), self.points],
            [self._formating('N° de téléphone :'), self.points],
            [self._formating('Adresse complète :'), self.points],
            ['', self.points],
            ['', self.points],
            [self._formating('Employeur :'), self.points],
        ]
        t = Table(data, colWidths=[4 * cm, 12 * cm], spaceAfter=0.7 * cm)
        t.hAlign = TA_LEFT
        t.setStyle(TableStyle(
            [
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        ))
        self.story.append(t)

        self.story.append(Paragraph('COORDONNÉES DE PAIEMENT', style_bold))
        data = [
            [self._formating('N° de ccp ou compte bancaire :'), self.points],
            [self._formating('Si banque, nom et adresse de celle-ci :'), self.points],
            [self._formating('ainsi que N° IBAN :'), self.points]
        ]
        t = Table(data, colWidths=[4 * cm, 12 * cm], spaceAfter=0.2 * cm)
        t.setStyle(TableStyle(
            [
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        ))
        t.hAlign = TA_LEFT
        self.story.append(t)

    def add_accounting_stamp(self, student, mandat=None):
        account = otp = total = ''
        if mandat == EXPERT_MANDAT:
            account = EXPERT_ACCOUNT
        elif mandat == MENTOR_MANDAT:
            account = MENTOR_ACCOUNT
            total = '500.-'

        if student.klass.is_Ede_pe():
            otp = OTP_EDE_PE_OTP
        elif student.klass.is_Ede_ps():
            otp = OTP_EDE_PS_OTP

        self.story.append((Paragraph(self.points * 2, style_normal)))
        self.story.append((Paragraph("A remplir par la comptabilité", style_normal)))
        self.story.append(Spacer(0, 0.5 * cm))
        if mandat == EXPERT_MANDAT:
            data = [
                ['Indemnités', 'Fr.'],
                ['Frais de déplacement', 'Fr.'],
                ['Repas', 'Fr.'],
                ['TOTAL', 'Fr.'],
            ]
            t = Table(data, colWidths=[4.5 * cm, 3 * cm], spaceBefore=0.5 * cm, spaceAfter=0.2 * cm)
            t.hAlign = TA_CENTER
            t.setStyle(TableStyle(
                [
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LINEBELOW', (1, 2), (2, 2), 0.5, colors.black),
                    ('LINEBELOW', (1, 3), (2, 3), 0.5, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                ]
            ))
            self.story.append(t)
        else:
            self.story.append(Spacer(0, 2 * cm))

        data = [['Visa chef de service:', "Donneur d'ordre et visa:", "Total en Fr:"]]
        t = Table(data, colWidths=[4 * cm, 4 * cm, 4 * cm], rowHeights=(1.2 * cm,))
        t.hAlign = TA_CENTER
        t.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        ))
        self.story.append(t)

        data = [
            ['No écriture', "Compte à débiter", "CC / OTP", " Montants"],
            ["Pièces annexées", account, otp, 'Fr.  {0}'.format(total)],
            ["Ordre", '', '', 'Fr.'],
            ["No fournisseur", '', '', 'Fr.'],
            ["Date scannage et visa", '', '', 'Fr.'],
        ]
        t = Table(data, colWidths=[3 * cm, 3 * cm, 3 * cm, 3 * cm])
        t.hAlign = TA_CENTER
        t.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        ))
        self.story.append(t)

    def add_adress(self, person):
        self.story.append(Spacer(0, 2 * cm))
        self.story.append(Paragraph(person.title, style_adress))
        self.story.append(Paragraph(person.full_name, style_adress))
        try:
            self.story.append(Paragraph(person.street, style_adress))
            self.story.append((Paragraph(person.pcode_city or '', style_adress)))
        except:
            self.story.append(Spacer(0, 1.8 * cm))


class ExpertEdeLetterPdf(EpcBaseDocTemplate):

    def __init__(self, student):
        self.student = student
        filename = slugify('{0}_{1}'.format(self.student.last_name, self.student.first_name)) + '_Expert.pdf'
        super().__init__(filename)

        first_page = PageTemplate(id='FisrtPage', frames=[self.page_frame], onPage=self.header)
        iso_page = PageTemplate(id='ISOPage', frames=[self.page_frame], onPage=self.header_iso)
        self.addPageTemplates([first_page, iso_page])
        self.story.append(NextPageTemplate(['*', 'ISOPage']))

    def produce(self):
        self.add_adress(self.student.expert)

        ptext = """
                <br/><br/><br/>
                La Chaux-de-Fonds, le {current_date}<br/>
                N/réf.:ASH/val<br/>
                <br/><br/><br/>
                <strong>Travail de diplôme</strong>
                <br/><br/><br/>
                {expert_title},<br/><br/>
                Vous avez accepté de fonctionner comme expert{expert_accord} pour un travail de diplôme de 
                l'un-e de nos étudiant-e-s. Nous vous remercions très chaleureusement de votre disponibilité.<br/><br/>
                En annexe, nous avons l'avantage de vous remettre le travail de {student_civility_full_name},
                ainsi que la grille d'évaluation commune aux deux membres du jury.<br/><br/>
                La soutenance de ce travail de diplôme se déroulera le:<br/>
                """
        self.story.append(Paragraph(ptext.format(
            current_date=django_format(date.today(), 'j F Y'),
            expert_title=self.student.expert.title,
            expert_accord=self.student.expert.adjective_ending,
            student_civility_full_name=self.student.civility_full_name,
        ), style_normal))

        ptext = "<br/>{0} à l'Ecole Santé-social Pierre-Coullery, salle {1}<br/><br/>"
        self.story.append(Paragraph(
                ptext.format(django_format(self.student.date_exam, 'l j F Y à H\hi'), self.student.room),
                style_bold_center
        ))

        ptext = """
                L'autre membre du jury sera {internal_expert_civility} {internal_expert_full_name}, 
                {internal_expert_role} dans notre école.<br/>
                <br/>
                Par ailleurs, nous nous permettons de vous faire parvenir en annexe le formulaire 
                «Indemnisation d'experts aux examens» que vous voudrez bien compléter au niveau des 
                «données privées / coordonnées de paiement» et nous retourner dans les meilleurs délais. <br/><br/>
                Restant à votre disposition pour tout complément d'information et en vous remerciant de
                l'attention que vous porterez à la présente, nous vous prions d'agréer, {expert_title}, 
                l'asurance de notre considération distinguée.<br/>
                <br/><br/><br/>
                La responsable de filière:<br/>
                <br/><br/>
                {resp_filiere}
                <br/><br/><br/>
                Annexes: ment.
                <br/><br/>
                Copies pour information: <br/>
                - {student_civility} {student_full_name}, {student_role} <br/>
                - {internal_expert_civility2} {internal_expert_full_name2}, {internal_expert_role2}
                """

        self.story.append(Paragraph(ptext.format(
            internal_expert_civility=self.student.internal_expert.civility,
            internal_expert_full_name=self.student.internal_expert.full_name,
            internal_expert_role=self.student.internal_expert.role,
            expert_title=self.student.expert.title,
            student_civility=self.student.civility,
            student_full_name=self.student.full_name,
            student_role=self.student.role,
            internal_expert_civility2=self.student.internal_expert.civility,
            internal_expert_full_name2=self.student.internal_expert.full_name,
            internal_expert_role2=self.student.internal_expert.role,
            resp_filiere=settings.RESP_FILIERE_EDE,
        ), style_normal))

        # ISO page
        self.story.append(PageBreak())
        self.story.append(NextPageTemplate('ISOPage'))

        self.add_private_data(self.student.expert)

        foo = "Mandat: Soutenance de {0} {1}, classe {2}".format(self.student.civility,
                                                                 self.student.full_name,
                                                                 self.student.klass)
        self.story.append(Paragraph(foo, style_normal))
        foo = "Date de l'examen : {0}".format(django_format(self.student.date_exam, 'l j F Y'))
        self.story.append(Paragraph(foo, style_normal))
        self.story.append(Spacer(0, 3 * cm))

        self.add_accounting_stamp(self.student, EXPERT_MANDAT)

        self.build(self.story)


class MentorCompensationPdfForm(EpcBaseDocTemplate):

    def __init__(self, student):
        self.student = student
        filename = slugify('{0}_{1}_{2}'.format(self.student.last_name, self.student.first_name, 'Mentor')) + '.pdf'
        super().__init__(filename)

        iso_page = PageTemplate(id='ISOPage', frames=[self.page_frame], onPage=self.header_iso)
        self.addPageTemplates([iso_page])

    def produce(self):
        self.add_private_data(self.student.mentor)

        foo = "Mandat: Mentoring de {0}, classe {1}".format(self.student.civility_full_name, self.student.klass)
        self.story.append(Paragraph(foo, style_normal))
        foo = "Fr 500.- forfaitaires payables après la session d'examen"
        self.story.append(Paragraph(foo, style_normal))
        self.story.append(Spacer(0, 3 * cm))

        self.add_accounting_stamp(self.student, MENTOR_MANDAT)

        self.build(self.story)


class ChargeSheetPDF(EpcBaseDocTemplate):
    """
    Génération des feuilles de charges en pdf.
    """
    def __init__(self, teacher):
        self.teacher = teacher
        filename = slugify('{0}_{1}'.format(teacher.last_name, teacher.first_name)) + '.pdf'
        super().__init__(filename)
        self.story = []
        first_page = PageTemplate(id='FisrtPage', frames=[self.page_frame], onPage=self.header)
        self.addPageTemplates([first_page])

    def produce(self, activities):

        self.add_adress(self.teacher)

        self.story.append(Paragraph(settings.CHARGE_SHEET_TITLE, style_bold))
        line = MCLine(450)
        self.story.append(line)

        data = list()
        data.append(["Report de l'année précédente", '{0:3d} pér.'.format(self.teacher.previous_report)])
        data.append(['Mandats', '{0:3d} pér.'.format(activities['tot_mandats'])])

        for act in activities['mandats']:
            data.append(['    * {0} ({1} pér.)'.format(act.subject, act.period)])

        data.append(['Enseignement (coef.2)', '{0:3d} pér.'.format(activities['tot_ens'])])
        data.append(['Formation continue et autres tâches', '{0:3d} pér.'.format(activities['tot_formation'])])
        data.append(['Total des heures travaillées', '{0:3d} pér.'.format(activities['tot_trav']),
                     '{0:4.1f} %'.format(activities['tot_trav']/settings.GLOBAL_CHARGE_PERCENT)])
        data.append(['Total des heures payées', '{0:3d} pér.'.format(activities['tot_paye']),
                     '{0:4.1f} %'.format(activities['tot_paye']/ settings.GLOBAL_CHARGE_PERCENT)])
        data.append(["Report à l'année prochaine", '{0:3d} pér.'.format(activities['report'])])

        t = Table(data, colWidths=[12*cm, 2*cm, 2*cm], rowHeights=(0.6*cm), spaceBefore=0.7 * cm, spaceAfter=1.5 * cm)
        t.setStyle(TableStyle(
            [
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, -3), (-1, -1), 0.5, colors.black),
                ('FONT', (0, -2), (-1, -2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]
        ))
        t.hAlign = TA_CENTER
        self.story.append(t)

        d = 'La Chaux-de-Fonds, le {0}'.format(django_format(date.today(), 'j F Y'))
        self.story.append(Paragraph(d, style_normal))
        self.story.append(Spacer(0, 0.5*cm))
        self.story.append(Paragraph('la direction', style_normal))

        cond1 = activities['tot_paye'] == settings.GLOBAL_CHARGE_TOTAL
        cond2 = activities['tot_paye'] != activities['tot_trav']
        if cond1 and cond2:
            self.story.append(Spacer(0, 1 * cm))
            d = 'Je soussigné-e déclare accepter les conditions ci-dessus pour la régularisation de mon salaire.'
            self.story.append(Paragraph(d, style_normal))
            self.story.append(Spacer(0, 1 * cm))
            self.story.append(Paragraph('Lieu, date et signature: ' + self.points, style_normal))

        self.build(self.story)


class UpdateDataFormPDF(EpcBaseDocTemplate):
    """
    Génération des formulaires PDF de mise à jour des données.
    """
    
    def __init__(self, path):
        super().__init__(path)
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

            data = [['Données enregistrées', 'Données corrigées et/ou complétées']]
            t = Table(data, colWidths=[8*cm, 8*cm], spaceBefore=0.2 * cm)
            t.setStyle(TableStyle(
                [
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ]
            ))
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

            t = Table(data, colWidths=[3*cm, 5*cm, 8*cm], hAlign=TA_CENTER)
            t.setStyle(TableStyle(
                [
                    ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
                ]
            ))
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
