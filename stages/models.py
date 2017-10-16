import json
from collections import OrderedDict
from datetime import date, timedelta

from django.conf import settings
from django.db import models

from . import utils


class Section(models.Model):
    """ Filières """
    name = models.CharField(max_length=20, verbose_name='Nom')

    class Meta:
        verbose_name = "Filière"

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=10, verbose_name='Nom')

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

    def __str__(self):
        return self.name

    def delta(self, diff):
        if diff == 0:
            return self
        try:
            return Level.objects.get(name=str(int(self.name)+diff))
        except Level.DoesNotExist:
            return None


class Klass(models.Model):
    name = models.CharField(max_length=10, verbose_name='Nom', unique=True)
    section = models.ForeignKey(Section, verbose_name='Filière', on_delete=models.PROTECT)
    level = models.ForeignKey(Level, verbose_name='Niveau', on_delete=models.PROTECT)
    teacher = models.ForeignKey('Teacher', blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name='Maître de classe')

    class Meta:
        verbose_name = "Classe"

    def __str__(self):
        return self.name


class Teacher(models.Model):
    civility = models.CharField(max_length=10, verbose_name='Civilité')
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    abrev = models.CharField(max_length=10, verbose_name='Sigle')
    birth_date = models.DateField(verbose_name='Date de naissance', blank=True, null=True)
    email = models.EmailField(verbose_name='Courriel', blank=True)
    contract = models.CharField(max_length=20, verbose_name='Contrat')
    rate = models.DecimalField(default=0.0, max_digits=4, decimal_places=1, verbose_name="Taux d'activité")
    ext_id = models.IntegerField(blank=True, null=True)
    previous_report = models.IntegerField(default=0, verbose_name='Report précédent')
    next_report = models.IntegerField(default=0, verbose_name='Report suivant')
    archived = models.BooleanField(default=False)

    class Meta:
        verbose_name='Enseignant'
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return '{0} {1}'.format(self.last_name, self.first_name)

    def calc_activity(self):
        """
        Return a dictionary of calculations relative to teacher courses.
        Store plus/minus periods to self.next_report.
        """
        mandats = self.course_set.filter(subject__startswith='#')
        ens = self.course_set.exclude(subject__startswith='#')
        tot_mandats = mandats.aggregate(models.Sum('period'))['period__sum'] or 0
        tot_ens = ens.aggregate(models.Sum('period'))['period__sum'] or 0
        # formation periods calculated at pro-rata of total charge
        tot_formation = int(round(
            (tot_mandats + tot_ens) / settings.MAX_ENS_PERIODS * settings.MAX_ENS_FORMATION
        ))
        tot_trav = self.previous_report + tot_mandats + tot_ens + tot_formation
        tot_paye = tot_trav
        max_periods = settings.MAX_ENS_PERIODS + settings.MAX_ENS_FORMATION
        # Special situations triggering reporting (positive or negative) hours for next year:
        #  - full-time teacher with a total charge under 100%
        #  - teachers with a total charge over 100%
        self.next_report = 0
        if (self.rate == 100 and tot_paye < max_periods) or (tot_paye > max_periods):
            tot_paye = max_periods
            self.next_report = tot_trav - tot_paye
        self.save()

        return {
            'mandats': mandats,
            'tot_mandats': tot_mandats,
            'tot_ens': tot_ens,
            'tot_formation': tot_formation,
            'tot_trav': tot_trav,
            'tot_paye': tot_paye,
            'report': self.next_report,
        }

    def calc_imputations(self):
        """
        Return a tuple for accountings charges
        """
        activities = self.calc_activity()
        imputations = OrderedDict(
            [('ASA', 0), ('ASSC', 0), ('ASE', 0), ('MP', 0), ('EDEpe', 0), ('EDEps', 0),
             ('EDS', 0), ('CAS_FPP', 0), ('Direction', 0)]
        )
        courses = self.course_set.all()

        for key in imputations:
            imputations[key] = courses.filter(imputation__contains=key).aggregate(models.Sum('period'))['period__sum'] or 0

        tot = sum(imputations.values())
        if tot > 0:
            for key in imputations:
                imputations[key] += round(imputations[key] / tot * activities['tot_formation'])

        # Split EDE periods in EDEpe and EDEps columns, in proportion
        ede = courses.filter(imputation='EDE').aggregate(models.Sum('period'))['period__sum'] or 0
        if ede > 0:
            pe = imputations['EDEpe']
            ps = imputations['EDEps']
            pe_percent = (pe / (pe + ps)) if (pe + ps) > 0 else 0.5
            pe_plus = round(ede * pe_percent)
            imputations['EDEpe'] += pe_plus
            imputations['EDEps'] += ede - pe_plus

        return (self.calc_activity(), imputations)


class Option(models.Model):
    name = models.CharField("Nom", max_length=100, unique=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    ext_id = models.IntegerField(null=True, unique=True, verbose_name='ID externe')
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    gender = models.CharField(max_length=3, blank=True, verbose_name='Genre')
    birth_date = models.DateField(blank=True, verbose_name='Date de naissance')
    street = models.CharField(max_length=150, blank=True, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    district = models.CharField(max_length=20, blank=True, verbose_name='Canton')
    tel = models.CharField(max_length=40, blank=True, verbose_name='Téléphone')
    mobile = models.CharField(max_length=40, blank=True, verbose_name='Portable')
    email = models.EmailField(verbose_name='Courriel', blank=True)
    avs = models.CharField(max_length=15, blank=True, verbose_name='No AVS')
    option_ase = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL)
    dispense_ecg = models.BooleanField(default=False)
    dispense_eps = models.BooleanField(default=False)
    soutien_dys = models.BooleanField(default=False)
    corporation = models.ForeignKey('Corporation', null=True, blank=True,
                                    on_delete=models.SET_NULL, verbose_name='Employeur')
    instructor = models.ForeignKey('CorpContact', null=True, blank=True,
                                   on_delete=models.SET_NULL, verbose_name='FEE/FPP')
    klass = models.ForeignKey(Klass, verbose_name='Classe', blank=True, null=True,
                              on_delete=models.PROTECT)
    archived = models.BooleanField(default=False, verbose_name='Archivé')
    archived_text = models.TextField(blank=True)

    support_tabimport = True

    class Meta:
        verbose_name = "Étudiant"

    def __str__(self):
        return '%s %s' % (self.last_name, self.first_name)

    @property
    def civility(self):
        return 'Monsieur' if self.gender == 'M' else 'Madame'

    @property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    @property
    def pcode_city(self):
        return '{0} {1}'.format(self.pcode, self.city)

    def save(self, **kwargs):
        if self.archived and not self.archived_text:
            # Fill archived_text with training data, JSON-formatted
            trainings = [
                tr.serialize() for tr in self.training_set.all().select_related('availability')
            ]
            self.archived_text = json.dumps(trainings)
        if self.archived_text and not self.archived:
            self.archived_text = ""
        super().save(**kwargs)

    def age_at(self, date_):
        """Return age of student at `date_` time, as a string."""
        age = (date.today() - self.birth_date) / timedelta(days=365.2425)
        age_y = int(age)
        age_m = int((age - age_y) * 12)
        return '%d ans%s' % (age_y, ' %d m.' % age_m if age_m > 0 else '')

    @classmethod
    def prepare_import(cls, student_values):
        """ Hook for tabimport, before new object get created """
        if 'klass' in student_values:
            try:
                k = Klass.objects.get(name=student_values['klass'])
            except Klass.DoesNotExist:
                raise Exception("La classe '%s' n'existe pas encore" % student_values['klass'])
            student_values['klass'] = k

        # See if postal code included in city, and split them
        if 'city' in student_values and utils.is_int(student_values['city'][:4]):
            student_values['pcode'], _, student_values['city'] = student_values['city'].partition(' ')
        student_values['archived'] = False
        return student_values


class Corporation(models.Model):
    ext_id = models.IntegerField(null=True, blank=True, verbose_name='ID externe')
    name = models.CharField(max_length=100, verbose_name='Nom')
    short_name = models.CharField(max_length=40, blank=True, verbose_name='Nom court')
    district = models.CharField(max_length=20, blank=True, verbose_name='Canton')
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name='Institution mère',
                               on_delete=models.SET_NULL)
    sector = models.CharField(max_length=40, blank=True, verbose_name='Secteur')
    typ = models.CharField(max_length=40, blank=True, verbose_name='Type de structure')
    street = models.CharField(max_length=100, blank=True, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    tel = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, verbose_name='Courriel')
    web = models.URLField(blank=True, verbose_name='Site Web')
    archived = models.BooleanField(default=False, verbose_name='Archivé')

    class Meta:
        verbose_name = "Institution"
        ordering = ('name',)
        unique_together = (('name', 'city'),)

    def __str__(self):
        sect = ' (%s)' % self.sector if self.sector else ''
        return "%s%s, %s %s" % (self.name, sect, self.pcode, self.city)

    @property
    def pcode_city(self):
        return '{0} {1}'.format(self.pcode, self.city)


class CorpContact(models.Model):
    corporation = models.ForeignKey(Corporation, verbose_name='Institution', on_delete=models.CASCADE)
    ext_id = models.IntegerField(null=True, blank=True, verbose_name='ID externe')
    is_main = models.BooleanField(default=False, verbose_name='Contact principal')
    always_cc = models.BooleanField(default=False, verbose_name='Toujours en copie')
    title = models.CharField(max_length=40, blank=True, verbose_name='Civilité')
    first_name = models.CharField(max_length=40, blank=True, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    role = models.CharField(max_length=40, blank=True, verbose_name='Fonction')
    tel = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.CharField(max_length=100, blank=True, verbose_name='Courriel')
    archived = models.BooleanField(default=False, verbose_name='Archivé')
    sections = models.ManyToManyField(Section, blank=True)

    class Meta:
        verbose_name = "Contact"

    def __str__(self):
        return '%s %s' % (self.last_name, self.first_name)


class Domain(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nom')

    class Meta:
        verbose_name = "Domaine"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Period(models.Model):
    """ Périodes de stages """
    title = models.CharField(max_length=150, verbose_name='Titre')
    section = models.ForeignKey(Section, verbose_name='Filière', on_delete=models.PROTECT,
                                limit_choices_to={'name__startswith': 'MP'})
    level = models.ForeignKey(Level, verbose_name='Niveau', on_delete=models.PROTECT)
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')

    class Meta:
        verbose_name = "Période de stage"
        ordering = ('-start_date',)

    def __str__(self):
        return '%s (%s)' % (self.dates, self.title)

    @property
    def dates(self):
        return '%s - %s' % (self.start_date, self.end_date)

    @property
    def school_year(self):
        return utils.school_year(self.start_date)

    @property
    def relative_level(self):
        """
        Return the level depending on current school year. For example, if the
        period is planned for next school year, level will be level - 1.
        """
        diff = (utils.school_year(self.start_date, as_tuple=True)[0] -
                utils.school_year(date.today(), as_tuple=True)[0])
        return self.level.delta(-diff)

    @property
    def weeks(self):
        """ Return the number of weeks of this period """
        return (self.end_date - self.start_date).days // 7


class Availability(models.Model):
    """ Disponibilités des institutions """
    corporation = models.ForeignKey(Corporation, verbose_name='Institution', on_delete=models.CASCADE)
    period = models.ForeignKey(Period, verbose_name='Période', on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, verbose_name='Domaine', on_delete=models.CASCADE)
    contact = models.ForeignKey(CorpContact, null=True, blank=True, verbose_name='Contact institution',
                                on_delete=models.SET_NULL)
    priority = models.BooleanField('Prioritaire', default=False)
    comment = models.TextField(blank=True, verbose_name='Remarques')

    class Meta:
        verbose_name = "Disponibilité"

    def __str__(self):
        return '%s - %s (%s) - %s' % (self.period, self.corporation, self.domain, self.contact)

    @property
    def free(self):
        try:
            self.training
        except Training.DoesNotExist:
            return True
        return False


class Training(models.Model):
    """ Stages """
    student = models.ForeignKey(Student, verbose_name='Étudiant', on_delete=models.CASCADE)
    availability = models.OneToOneField(Availability, verbose_name='Disponibilité', on_delete=models.CASCADE)
    referent = models.ForeignKey(Teacher, null=True, blank=True, verbose_name='Référent',
                                 on_delete=models.SET_NULL)
    comment = models.TextField(blank=True, verbose_name='Remarques')

    class Meta:
        verbose_name = "Stage"
        ordering = ("-availability__period",)

    def __str__(self):
        return '%s chez %s (%s)' % (self.student, self.availability.corporation, self.availability.period)

    def serialize(self):
        """
        Compute a summary of the training as a dict representation (for archiving purpose).
        """
        return {
            'period': str(self.availability.period),
            'corporation': str(self.availability.corporation),
            'referent': str(self.referent),
            'comment': self.comment,
            'contact': str(self.availability.contact),
            'comment_avail': self.availability.comment,
            'domain': str(self.availability.domain),
        }


IMPUTATION_CHOICES = (
    ('ASAFE', 'ASAFE'),
    ('ASEFE', 'ASEFE'),
    ('ASSCFE', 'ASSCFE'),
    ('MP', 'MP'),
    ('EDEpe', 'EDEpe'),
    ('EDEps', 'EDEps'),
    ('EDE', 'EDE'),
    ('EDS', 'EDS'),
    ('CAS_FPP', 'CAS_FPP'),
)


class Course(models.Model):
    """Cours et mandats attribués aux enseignants"""
    teacher = models.ForeignKey(Teacher, blank=True, null=True,
                                verbose_name="Enseignant-e", on_delete=models.SET_NULL)
    public = models.CharField("Classe(s)", max_length=200, default='')
    subject = models.CharField("Sujet", max_length=100, default='')
    period = models.IntegerField("Nb de périodes", default=0)
    # Imputation comptable: compte dans lequel les frais du cours seront imputés
    imputation = models.CharField("Imputation", max_length=10, choices=IMPUTATION_CHOICES)

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'

    def __str__(self):
        return '{0} - {1} - {2} - {3}'.format(
            self.teacher, self.public, self.subject, self.period
        )

GENDER_CHOICES = (
    ('M', 'Masculin'),
    ('F', 'Féminin'),
    ('I', 'Inconnu')
)

SECTION_CHOICES = (
    ('ASA', 'Aide en soin et accompagnement AFP'),
    ('ASE', 'Assist. socio-éducatif-ve CFC'),
    ('ASSC', 'Assist. en soin et santé communautaire CFC'),
    ('EDE', 'Educ. de l\'enfance, dipl. ES'),
    ('EDS', 'Educ. social-e, dipl. ES'),
)


OPTION_CHOICES = (
    ('GEN', 'Généraliste'),
    ('ENF', 'Enfance'),
    ('PAG', 'Personnes âgées'),
    ('HAN', 'Handicap'),
    ('PE-5400h', 'Parcours Emploi 5400h.'),
    ('PE-3600h', 'Parcours Emploi 3600h.'),
    ('PS', 'Parcours stage'),
)


class Config(models.Model):
    key = models.CharField(max_length=100)
    value = models.TextField()
    comment = models.TextField()

    def __str__(self):
        return '{0} : {1}'.format(self.key, self.value)


class District(models.Model):
    class Meta:
        verbose_name = 'Canton'

    abrev = models.CharField(max_length=10)
    name = models.CharField(max_length=30)

    def __str__(self):
        return '{0} - {1}'.format(self.abrev, self.name)


class Candidate(models.Model):
    """
    Inscriptions for new students
    """
    first_name = models.CharField(max_length=40, verbose_name='Prénom')
    last_name = models.CharField(max_length=40, verbose_name='Nom')
    gender = models.CharField(max_length=3, choices=GENDER_CHOICES, verbose_name='Genre')
    birth_date = models.DateField(default=None, blank=True, null=True, verbose_name='Date de naissance')
    street = models.CharField(max_length=150, blank=True, verbose_name='Rue')
    pcode = models.CharField(max_length=4, verbose_name='Code postal')
    city = models.CharField(max_length=40, verbose_name='Localité')
    district = models.ForeignKey(District, default=None, null=True, verbose_name='Canton')
    mobile = models.CharField(max_length=40, blank=True, verbose_name='Portable')
    email = models.EmailField(verbose_name='Courriel', blank=True)
    avs = models.CharField(max_length=15, blank=True, verbose_name='No AVS')
    handicap = models.BooleanField(default=False)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES, null=False, verbose_name='Filière')
    option = models.CharField(max_length=20, choices=OPTION_CHOICES, null=True, blank=True)
    exemption_ecg = models.BooleanField(default=False)
    validation_sfpo = models.DateField(default=None, blank=True, null=True, verbose_name='Confirmation SFPO')
    integration_second_year = models.BooleanField(default=False, verbose_name='Intégration')
    date_confirmation_mail = models.DateField(default=None, blank=True, null=True, verbose_name='Mail de confirmation')
    canceled_file = models.BooleanField(default=False, verbose_name='Dossier retiré')
    photo = models.BooleanField(default=False)
    corporation = models.ForeignKey('Corporation', null=True, blank=True,
                                    on_delete=models.SET_NULL, verbose_name='Employeur')
    instructor = models.ForeignKey('CorpContact', null=True, blank=True,
                                   on_delete=models.SET_NULL, verbose_name='FEE/FPP')

    # Checking for registration file
    registration_form = models.BooleanField(default=False, verbose_name="Formulaire d'inscription")
    certificate_of_payement = models.BooleanField(default=False, verbose_name="Attest. paiement")
    police_record = models.BooleanField(default=False, verbose_name="Casier judic.")
    cv = models.BooleanField(default=False, verbose_name="CV")
    certif_of_cfc = models.BooleanField(default=False, verbose_name="CFC")
    certif_of_800h = models.BooleanField(default=False, verbose_name="Attest. 800h.")
    reflexive_text = models.BooleanField(default=False, verbose_name="Texte réflexif")
    promise = models.BooleanField(default=False, verbose_name="Promesse d'eng.")
    contract = models.BooleanField(default=False, verbose_name="Contrat valide")
    comment = models.TextField(default='', blank=True, verbose_name='Remarques')

    proc_admin_ext = models.BooleanField(default=False, verbose_name="Insc. autre école")
    work_certificate = models.BooleanField(default=False, verbose_name="Certif. de travail")
    marks_certificate = models.BooleanField(default=False, verbose_name="Bull. notes")
    deposite_date = models.DateField(default=None, blank=True, null=True, verbose_name='Date dépôt dossier')
    interview_date = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Date entretien prof.')
    interview_room = models.CharField(max_length=50, blank=True, verbose_name="Salle d'entretien prof.")
    examination_result = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Points examen')
    interview_result = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Points entretien prof.')
    file_result = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Points dossier')
    total_result_points = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Total points')
    total_result_mark = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Note finale')
    accepted = models.BooleanField(default=False, verbose_name='Admis')
    interview_resp = models.ForeignKey(Teacher, default=None, null=True, blank=True, verbose_name='Exp. entretien')
    file_resp = models.ForeignKey(Teacher, default=None, related_name='rel_file_exp', null=True,
                                  blank=True, verbose_name='Exp. dossier')

    class Meta:
        verbose_name = 'Candidat'

    @property
    def civility(self):
        if self.gender == 'M':
            return 'Monsieur'
        if self.gender == 'F':
            return 'Madame'
        else:
            return ''

    def confirm_email(self):
        if self.date_confirmation_mail is None:
            return u'<img src="{0}" height="20px" width="20px" />'.format('/static/img/no_ok.jpg')
        else:
            return u'<img src="{0}" height="20px" width="20px" />'.format('/static/img/ok.jpeg')

    confirm_email.allow_tags = True
