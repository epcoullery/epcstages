import os
import tempfile

from datetime import date
from django.conf import settings
from django.contrib.staticfiles.finders import find

from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                PageBreak, Table, TableStyle, Image)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle as PS

style_normal = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment = TA_LEFT)
style_bold = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=10, alignment = TA_LEFT)
style_title = PS(name='CORPS', fontName='Helvetica-Bold', fontSize=12, alignment = TA_LEFT, spaceBefore=2*cm)
style_adress = PS(name='CORPS', fontName='Helvetica', fontSize=10, alignment = TA_LEFT, leftIndent=280)
style_normal_right = PS(name='CORPS', fontName='Helvetica', fontSize=8, alignment = TA_RIGHT)


class ChargeSheetPDF(SimpleDocTemplate):
    """
    Génération des feuilles de charges en pdf.
    """

    def __init__(self, teacher):
        self.teacher = teacher
        filename = '{0}_{1}.pdf'.format(teacher.last_name, teacher.first_name)
        path = os.path.join(tempfile.gettempdir(), filename)
        super().__init__(path, pagesize=A4, topMargin=0*cm, leftMargin=2*cm)

    def produce(self, activities):
        self.story = []
        self.story.append(Image(find('img/header.gif'), width=520, height=75))
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
        self.story.append(PageBreak())
        self.build(self.story)


class UpdateDataFormPDF(SimpleDocTemplate):
    """
    Génération des formulaires PDF de mise à jour des données.
    """
    def __init__(self, path):
        super().__init__(path, pagesize=A4, topMargin=0*cm, leftMargin=2*cm)
        self.text = "Afin de mettre à jour nos bases de données, nous vous serions reconnaissant "
        self.text += "de contrôler les données ci-dessous qui vous concernent selon votre filière "
        self.text += "et de retourner le présent document corrigé et complété à votre maître de classe jusqu'au "
        self.text += "vendredi 9 septembre prochain.<br/><br/>"
        self.text += "Nous vous remercions de votre précieuse collaboration.<br/><br/>"
        self.text += "Le secrétariat"
        self.underline = '__________________________________'
        
    def produce(self, klass):
        self.story = []
        for student in klass.student_set.all():
            self.story.append(Image(find('img/header.gif'), width=520, height=75))
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
            data = [['NOM', student.last_name, self.underline]]
            data.append(['PRENOM', student.first_name, self.underline])
            data.append(['ADRESSE', student.street, self.underline])
            data.append(['LOCALITE', student.pcode_city, self.underline])
            data.append(['MOBILE', student.mobile, self.underline])
            data.append(['CLASSE', student.klass, self.underline])
            data.append(['', '', ''])
            
            # Corporation data
            corp_required = self.is_corp_required(student.klass.name)
            if corp_required:
                if student.corporation is None:
                    data.append(["Données de l'Employeur", '', ''])
                    data.append(['NOM', '', self.underline])
                    data.append(['ADRESSE', '', self.underline])
                    data.append(['LOCALITE', '', self.underline])
                    data.append(['', '', ''])
                else:
                    data.append(["Données de l'Employeur", '', ''])
                    data.append(['NOM', student.corporation.name, self.underline])
                    data.append(['ADRESSE', student.corporation.street, self.underline])
                    data.append(['LOCALITE', student.corporation.pcode_city(), self.underline])
                    data.append(['', '', ''])

            # Instructor data
            instr_required = self.is_instr_required(student.klass.name)
            if instr_required:
                if student.instructor is None:
                    data.append(['Données du FEE/FPP (personne de contact pour les informations)', '', ''])
                    data.append(['NOM', '', self.underline])
                    data.append(['PRENOM', '', self.underline])
                    data.append(['TELEPHONE', '', self.underline])
                    data.append(['E-MAIL', '', self.underline])
                else:
                    data.append(['Données du FEE/FPP (personne de contact pour les informations)', '', ''])
                    data.append(['NOM', student.instructor.last_name, self.underline])
                    data.append(['PRENOM', student.instructor.first_name, self.underline])
                    data.append(['TELEPHONE', student.instructor.tel, self.underline])
                    data.append(['E-MAIL', student.instructor.email, self.underline])

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

    def is_corp_required(self, klass_name):
        for el in ['FE', 'EDS', 'EDEpe']:
            if el in klass_name:
                return True
        return False

    def is_instr_required(self, klass_name):
        for el in ['FE', 'EDS']:
            if el in klass_name:
                return True
        return False
