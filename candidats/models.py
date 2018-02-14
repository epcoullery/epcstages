from django.db import models
from django.db.models import Q
from django.utils.dateformat import format as django_format

from stages.models import Corporation, CorpContact, Teacher

GENDER_CHOICES = (
    ('M', 'Masculin'),
    ('F', 'Féminin'),
    ('I', 'Inconnu')
)

SECTION_CHOICES = (
    ('ASA', 'Aide en soin et accompagnement AFP'),
    ('ASE', 'Assist. socio-éducatif-ve CFC'),
    ('ASSC', 'Assist. en soin et santé communautaire CFC'),
    ('EDE', "Education de l'enfance, dipl. ES"),
    ('EDS', 'Education sociale, dipl. ES'),
)

OPTION_CHOICES = (
    ('GEN', 'Généraliste'),
    ('ENF', 'Enfance'),
    ('PAG', 'Personnes âgées'),
    ('HAN', 'Handicap'),
    ('PE-5400h', 'Parcours Emploi 5400h.'),
    ('PE-3600h', 'Parcours Emploi 3600h.'),
    ('PS', 'Parcours stage 5400h.'),
)

DIPLOMA_CHOICES = (
    (0, 'Aucun'),
    (1, "CFC d'ASE"),
    (2, "CFC autre domaine"),
    (3, "Matu acad./spéc. ou dipl. ECG"),
    (4, "Portfolio"),
)

DIPLOMA_STATUS_CHOICES = (
    (0, 'Inconnu'),
    (1, 'En cours'),
    (2, 'OK'),
)

RESIDENCE_PERMITS_CHOICES = (
    (0, 'Pas nécessaire'),
    (1, 'Nécessaire - OK'),
    (2, 'Manquante'),
)

AES_ACCORDS_CHOICES = (
    (0, 'OK'),
    (1, 'Demander accord du canton concerné'),
    (2, 'Refus du canton concerné')
)


class Candidate(models.Model):
    """
    Inscriptions for new students
    """
    first_name = models.CharField('Prénom', max_length=40)
    last_name = models.CharField('Nom', max_length=40)
    gender = models.CharField('Genre', max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField('Date de naissance', blank=True, null=True)
    street = models.CharField('Rue', max_length=150, blank=True)
    pcode = models.CharField('Code postal', max_length=4)
    city = models.CharField('Localité', max_length=40)
    district = models.CharField('Canton', max_length=2, blank=True)
    mobile = models.CharField('Portable', max_length=40, blank=True)
    email = models.EmailField('Courriel', blank=True)
    avs = models.CharField('No AVS', max_length=15, blank=True)
    handicap = models.BooleanField(default=False)

    section = models.CharField('Filière', max_length=10, choices=SECTION_CHOICES)
    option = models.CharField('Option', max_length=20, choices=OPTION_CHOICES, blank=True)
    exemption_ecg = models.BooleanField(default=False)
    validation_sfpo = models.DateField('Confirmation SFPO', blank=True, null=True)
    integration_second_year = models.BooleanField('Intégration', default=False)
    confirmation_date = models.DateTimeField('Envoi mail de confirmation', blank=True, null=True)
    canceled_file = models.BooleanField('Dossier retiré', default=False)
    has_photo = models.BooleanField(default=False, verbose_name='Photo passeport')

    corporation = models.ForeignKey(
        Corporation, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Employeur'
    )
    instructor = models.ForeignKey(
        CorpContact, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='FEE/FPP'
    )

    # Checking for registration file
    registration_form = models.BooleanField("Formulaire d'inscription", default=False)
    certificate_of_payement = models.BooleanField("Attest. de paiement", default=False)
    police_record = models.BooleanField("Casier judic.", default=False)
    cv = models.BooleanField("CV", default=False)
    reflexive_text = models.BooleanField("Texte réflexif", default=False)
    promise = models.BooleanField("Promesse d'eng.", default=False)
    contract = models.BooleanField("Contrat valide", default=False)
    comment = models.TextField('Remarques', blank=True)

    work_certificate = models.BooleanField("Bilan act. prof./dernier stage", default=False)
    marks_certificate = models.BooleanField("Bull. de notes", default=False)
    deposite_date = models.DateField('Date dépôt dossier')

    examination_result = models.PositiveSmallIntegerField('Points examen', blank=True, null=True)
    interview_result = models.PositiveSmallIntegerField('Points entretien prof.', blank=True, null=True)
    file_result = models.PositiveSmallIntegerField('Points dossier', blank=True, null=True)
    total_result_points = models.PositiveSmallIntegerField('Total points', blank=True, null=True)
    total_result_mark = models.PositiveSmallIntegerField('Note finale', blank=True, null=True)

    inscr_other_school = models.CharField("Inscr. autre école", max_length=30, blank=True)
    certif_of_800_childhood = models.BooleanField("Attest. 800h. enfance", default=False)
    certif_of_800_general = models.BooleanField("Attest. 800h. général", default=False)
    diploma = models.PositiveSmallIntegerField('Titre sec. II', choices=DIPLOMA_CHOICES, default=0)
    diploma_detail = models.CharField('Détail titre', max_length=30, blank=True, default='')
    diploma_status = models.PositiveSmallIntegerField("Statut titre", choices=DIPLOMA_STATUS_CHOICES, default=0)
    activity_rate = models.CharField("Taux d'activité", max_length=50, blank=True,  default='')
    validation_date = models.DateTimeField('Envoi mail de validation', null=True, blank=True)
    convocation_date = models.DateTimeField('Envoi mail de confirmation', null=True, blank=True)

    aes_accords = models.PositiveSmallIntegerField("Accord AES", choices=AES_ACCORDS_CHOICES, default=0)
    residence_permits = models.PositiveSmallIntegerField(
        "Autor. de séjour (pour les pers. étrang.)",
        choices=RESIDENCE_PERMITS_CHOICES, blank=True, null=True, default=0
    )

    accepted = models.BooleanField('Admis', default=False)

    examination_teacher = models.ForeignKey(Teacher, null=True, blank=True, default=None,
                                            on_delete=models.SET_NULL,
                                            limit_choices_to=Q(abrev='MME') | Q(abrev='CLG'),
                                            verbose_name='Correct. dossier')

    class Meta:
        verbose_name = 'Candidat'

    def __str__(self):
        return "%s %s" % (self.last_name, self.first_name)

    @property
    def civility(self):
        if self.gender == 'M':
            return 'Monsieur'
        if self.gender == 'F':
            return 'Madame'
        else:
            return ''

    @property
    def section_option(self):
        if not self.option:
            return self.get_section_display()
        else:
            return '{0}, option «{1}»'.format(self.get_section_display(), self.get_option_display())

    def get_ok(self, fieldname):
        return 'OK' if getattr(self, fieldname) is True else 'NON'


INTERVIEW_CHOICES = (
    ('N', 'Normal'),
    ('R', 'Réserve'),
    ('X', 'Attente confirmation enseignants'),
)

class Interview(models.Model):
    date = models.DateTimeField('Date')
    room = models.CharField("Salle d'entretien", max_length=20)
    candidat = models.OneToOneField(Candidate, null=True, blank=True, on_delete=models.SET_NULL)
    teacher_int = models.ForeignKey(
        Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
        verbose_name='Ens. entretien'
    )
    teacher_file = models.ForeignKey(
        Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
        verbose_name='Ens. dossier'
    )
    status = models.CharField('Statut', max_length=1, choices=INTERVIEW_CHOICES, default='N')

    class Meta:
        verbose_name = "Entretien d'admission"
        verbose_name_plural = "Entretiens d'admission"
        ordering = ('date',)

    def __str__(self):
        return '{0} : {1} (Ent.) / {2} (Dos.) - ({3}) -salle:{4}-{5}'.format(
            self.date_formatted,
            self.teacher_int.abrev if self.teacher_int else '?',
            self.teacher_file.abrev if self.teacher_file else '?',
            self.status, self.room, self.candidat or '???'
        )

    @property
    def date_formatted(self):
        return django_format(self.date, "l j F Y à H\hi")
