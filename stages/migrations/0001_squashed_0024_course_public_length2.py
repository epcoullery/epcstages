from django.db import migrations, models
import django.db.migrations.operations.special
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.BooleanField(default=False, verbose_name='Prioritaire')),
                ('comment', models.TextField(blank=True, verbose_name='Remarques')),
            ],
            options={
                'verbose_name': 'Disponibilité',
            },
        ),
        migrations.CreateModel(
            name='CorpContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext_id', models.IntegerField(blank=True, null=True, verbose_name='ID externe')),
                ('is_main', models.BooleanField(default=False, verbose_name='Contact principal')),
                ('always_cc', models.BooleanField(default=False, verbose_name='Toujours en copie')),
                ('title', models.CharField(blank=True, max_length=40, verbose_name='Civilité')),
                ('first_name', models.CharField(blank=True, max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('role', models.CharField(blank=True, max_length=40, verbose_name='Fonction')),
                ('tel', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('email', models.CharField(blank=True, max_length=100, verbose_name='Courriel')),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
            ],
            options={
                'verbose_name': 'Contact',
            },
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext_id', models.IntegerField(blank=True, null=True, verbose_name='ID externe')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('short_name', models.CharField(blank=True, max_length=40, verbose_name='Nom court')),
                ('district', models.CharField(blank=True, max_length=20, verbose_name='Canton')),
                ('sector', models.CharField(blank=True, max_length=40, verbose_name='Secteur')),
                ('typ', models.CharField(blank=True, max_length=40, verbose_name='Type de structure')),
                ('street', models.CharField(blank=True, max_length=100, verbose_name='Rue')),
                ('pcode', models.CharField(max_length=4, verbose_name='Code postal')),
                ('city', models.CharField(max_length=40, verbose_name='Localité')),
                ('tel', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Courriel')),
                ('web', models.URLField(blank=True, verbose_name='Site Web')),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Corporation', verbose_name='Institution mère')),
            ],
            options={
                'verbose_name': 'Institution',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public', models.CharField(default='', max_length=200, verbose_name='Classe(s)')),
                ('subject', models.CharField(default='', max_length=100, verbose_name='Sujet')),
                ('period', models.IntegerField(default=0, verbose_name='Nb de périodes')),
                ('imputation', models.CharField(choices=[('ASAFE', 'ASAFE'), ('ASEFE', 'ASEFE'), ('ASSCFE', 'ASSCFE'), ('MP', 'MP'), ('EDEpe', 'EDEpe'), ('EDEps', 'EDEps'), ('EDE', 'EDE'), ('EDS', 'EDS'), ('CAS_FPP', 'CAS_FPP')], max_length=10, verbose_name='Imputation')),
            ],
            options={
                'verbose_name_plural': 'Cours',
                'verbose_name': 'Cours',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Domaine',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Classe',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Niveaux',
                'verbose_name': 'Niveau',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Titre')),
                ('start_date', models.DateField(verbose_name='Date de début')),
                ('end_date', models.DateField(verbose_name='Date de fin')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stages.Level', verbose_name='Niveau')),
            ],
            options={
                'verbose_name': 'Période de stage',
                'ordering': ('-start_date',),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Filière',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext_id', models.IntegerField(null=True, unique=True, verbose_name='ID externe')),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Masculin'), ('F', 'Féminin')], max_length=3, verbose_name='Genre')),
                ('birth_date', models.DateField(blank=True, verbose_name='Date de naissance')),
                ('street', models.CharField(blank=True, max_length=150, verbose_name='Rue')),
                ('pcode', models.CharField(max_length=4, verbose_name='Code postal')),
                ('city', models.CharField(max_length=40, verbose_name='Localité')),
                ('district', models.CharField(blank=True, max_length=20, verbose_name='Canton')),
                ('tel', models.CharField(blank=True, max_length=40, verbose_name='Téléphone')),
                ('mobile', models.CharField(blank=True, max_length=40, verbose_name='Portable')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Courriel')),
                ('avs', models.CharField(blank=True, max_length=15, verbose_name='No AVS')),
                ('dispense_ecg', models.BooleanField(default=False)),
                ('dispense_eps', models.BooleanField(default=False)),
                ('soutien_dys', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False, verbose_name='Archivé')),
                ('archived_text', models.TextField(blank=True)),
                ('corporation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Corporation', verbose_name='Employeur')),
                ('instructor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.CorpContact', verbose_name='FEE/FPP')),
                ('klass', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='stages.Klass', verbose_name='Classe')),
            ],
            options={
                'verbose_name': 'Étudiant',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('civility', models.CharField(max_length=10, choices=[('Madame', 'Madame'), ('Monsieur', 'Monsieur')], verbose_name='Civilité')),
                ('first_name', models.CharField(max_length=40, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=40, verbose_name='Nom')),
                ('abrev', models.CharField(max_length=10, verbose_name='Sigle')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Date de naissance')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Courriel')),
                ('contract', models.CharField(max_length=20, verbose_name='Contrat')),
                ('rate', models.DecimalField(decimal_places=1, default=0.0, max_digits=4, verbose_name="Taux d'activité")),
                ('ext_id', models.IntegerField(blank=True, null=True)),
                ('previous_report', models.IntegerField(default=0, verbose_name='Report précédent')),
                ('next_report', models.IntegerField(default=0, verbose_name='Report suivant')),
                ('archived', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Enseignant',
                'ordering': ('last_name', 'first_name'),
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, verbose_name='Remarques')),
                ('availability', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stages.Availability', verbose_name='Disponibilité')),
                ('referent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Référent')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Student', verbose_name='Étudiant')),
            ],
            options={
                'verbose_name': 'Stage',
                'ordering': ('-availability__period',),
            },
        ),
        migrations.AddField(
            model_name='period',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stages.Section', verbose_name='Filière'),
        ),
        migrations.AddField(
            model_name='klass',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stages.Level', verbose_name='Niveau'),
        ),
        migrations.AddField(
            model_name='klass',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stages.Section', verbose_name='Filière'),
        ),
        migrations.AddField(
            model_name='klass',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Maître de classe'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Enseignant-e'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='corporation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Corporation', verbose_name='Institution'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='sections',
            field=models.ManyToManyField(blank=True, to='stages.Section'),
        ),
        migrations.AddField(
            model_name='availability',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.CorpContact', verbose_name='Contact institution'),
        ),
        migrations.AddField(
            model_name='availability',
            name='corporation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Corporation', verbose_name='Institution'),
        ),
        migrations.AddField(
            model_name='availability',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Domain', verbose_name='Domaine'),
        ),
        migrations.AddField(
            model_name='availability',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Period', verbose_name='Période'),
        ),
        migrations.AlterUniqueTogether(
            name='corporation',
            unique_together=set([('name', 'city')]),
        ),
    ]
