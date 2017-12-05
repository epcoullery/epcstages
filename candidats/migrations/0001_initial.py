from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stages', '0002_add_student_option_ase'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('gender', models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('I', 'Inconnu')], max_length=1, verbose_name='Genre')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Date de naissance')),
                ('street', models.CharField(blank=True, max_length=150, verbose_name='Rue')),
                ('pcode', models.CharField(max_length=4, verbose_name='Code postal')),
                ('city', models.CharField(max_length=40, verbose_name='Localité')),
                ('district', models.CharField(blank=True, max_length=2, verbose_name='Canton')),
                ('mobile', models.CharField(blank=True, max_length=40, verbose_name='Portable')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Courriel')),
                ('avs', models.CharField(blank=True, max_length=15, verbose_name='No AVS')),
                ('handicap', models.BooleanField(default=False)),
                ('section', models.CharField(choices=[('ASA', 'Aide en soin et accompagnement AFP'), ('ASE', 'Assist. socio-éducatif-ve CFC'), ('ASSC', 'Assist. en soin et santé communautaire CFC'), ('EDE', "Educ. de l'enfance, dipl. ES"), ('EDS', 'Educ. social-e, dipl. ES')], max_length=10, verbose_name='Filière')),
                ('option', models.CharField(blank=True, choices=[('GEN', 'Généraliste'), ('ENF', 'Enfance'), ('PAG', 'Personnes âgées'), ('HAN', 'Handicap'), ('PE-5400h', 'Parcours Emploi 5400h.'), ('PE-3600h', 'Parcours Emploi 3600h.'), ('PS', 'Parcours stage')], max_length=20, verbose_name='Option')),
                ('exemption_ecg', models.BooleanField(default=False)),
                ('validation_sfpo', models.DateField(blank=True, null=True, verbose_name='Confirmation SFPO')),
                ('integration_second_year', models.BooleanField(default=False, verbose_name='Intégration')),
                ('date_confirmation_mail', models.DateField(blank=True, null=True, verbose_name='Mail de confirmation')),
                ('canceled_file', models.BooleanField(default=False, verbose_name='Dossier retiré')),
                ('has_photo', models.BooleanField(default=False, verbose_name='Photo')),
                ('registration_form', models.BooleanField(default=False, verbose_name="Formulaire d'inscription")),
                ('certificate_of_payement', models.BooleanField(default=False, verbose_name='Attest. paiement')),
                ('police_record', models.BooleanField(default=False, verbose_name='Casier judic.')),
                ('cv', models.BooleanField(default=False, verbose_name='CV')),
                ('certif_of_cfc', models.BooleanField(default=False, verbose_name='CFC')),
                ('certif_of_800h', models.BooleanField(default=False, verbose_name='Attest. 800h.')),
                ('reflexive_text', models.BooleanField(default=False, verbose_name='Texte réflexif')),
                ('promise', models.BooleanField(default=False, verbose_name="Promesse d'eng.")),
                ('contract', models.BooleanField(default=False, verbose_name='Contrat valide')),
                ('comment', models.TextField(blank=True, verbose_name='Remarques')),
                ('proc_admin_ext', models.BooleanField(default=False, verbose_name='Insc. autre école')),
                ('work_certificate', models.BooleanField(default=False, verbose_name='Certif. de travail')),
                ('marks_certificate', models.BooleanField(default=False, verbose_name='Bull. notes')),
                ('deposite_date', models.DateField(blank=True, null=True, verbose_name='Date dépôt dossier')),
                ('interview_date', models.DateTimeField(blank=True, null=True, verbose_name='Date entretien prof.')),
                ('interview_room', models.CharField(blank=True, max_length=50, verbose_name="Salle d'entretien prof.")),
                ('examination_result', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Points examen')),
                ('interview_result', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Points entretien prof.')),
                ('file_result', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Points dossier')),
                ('total_result_points', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Total points')),
                ('total_result_mark', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Note finale')),
                ('accepted', models.BooleanField(default=False, verbose_name='Admis')),
                ('corporation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Corporation', verbose_name='Employeur')),
                ('file_resp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Exp. dossier')),
                ('instructor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.CorpContact', verbose_name='FEE/FPP')),
                ('interview_resp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Exp. entretien')),
            ],
            options={
                'verbose_name': 'Candidat',
            },
        ),
    ]
