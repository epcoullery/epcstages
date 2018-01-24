from django.db import models


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
    date_confirmation_mail = models.DateField('Mail de confirmation', blank=True, null=True)
    canceled_file = models.BooleanField('Dossier retiré', default=False)
    has_photo = models.BooleanField(default=False, verbose_name='Photo passeport')

    corporation = models.ForeignKey(
        'stages.Corporation', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Employeur'
    )
    instructor = models.ForeignKey(
        'stages.CorpContact', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='FEE/FPP'
    )

    # Checking for registration file
    registration_form = models.BooleanField("Formulaire d'inscription", default=False)
    certificate_of_payement = models.BooleanField("Attest. de paiement", default=False)
    police_record = models.BooleanField("Casier judic.", default=False)
    cv = models.BooleanField("CV", default=False)
    certif_of_cfc = models.BooleanField("Attest. CFC", default=False)
    certif_of_800h = models.BooleanField("Attest. 800h.", default=False)
    reflexive_text = models.BooleanField("Texte réflexif", default=False)
    promise = models.BooleanField("Promesse d'eng.", default=False)
    contract = models.BooleanField("Contrat valide", default=False)
    comment = models.TextField('Remarques', blank=True)

    proc_admin_ext = models.BooleanField("Insc. autre école", default=False)
    work_certificate = models.BooleanField("Certif. de travail", default=False)
    marks_certificate = models.BooleanField("Bull. de notes", default=False)
    deposite_date = models.DateField('Date dépôt dossier')
    interview_date = models.DateTimeField('Date entretien prof.', blank=True, null=True)
    interview_room = models.CharField("Salle d'entretien prof.", max_length=50, blank=True)
    examination_result = models.PositiveSmallIntegerField('Points examen', blank=True, null=True)
    interview_result = models.PositiveSmallIntegerField('Points entretien prof.', blank=True, null=True)
    file_result = models.PositiveSmallIntegerField('Points dossier', blank=True, null=True)
    total_result_points = models.PositiveSmallIntegerField('Total points', blank=True, null=True)
    total_result_mark = models.PositiveSmallIntegerField('Note finale', blank=True, null=True)

    accepted = models.BooleanField('Admis', default=False)
    interview_resp = models.ForeignKey(
        'stages.Teacher', null=True, blank=True, related_name='+', verbose_name='Exp. entretien',
        on_delete=models.SET_NULL
    )
    file_resp = models.ForeignKey(
        'stages.Teacher', null=True, blank=True, related_name='+', verbose_name='Exp. dossier',
        on_delete=models.SET_NULL
    )

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
