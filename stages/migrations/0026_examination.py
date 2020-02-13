from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0025_section_has_stages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Examination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_exam', models.DateTimeField(blank=True, null=True)),
                ('room', models.CharField(blank=True, max_length=15, verbose_name='Salle')),
                ('mark', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Note')),
                ('mark_acq', models.CharField(blank=True, choices=[('non', 'Non acquis'), ('part', 'Partiellement acquis'), ('acq', 'Acquis')], max_length=5, verbose_name='Note')),
                ('date_soutenance_mailed', models.DateTimeField(blank=True, null=True, verbose_name='Convoc. env.')),
                ('date_confirm_received', models.DateTimeField(blank=True, null=True, verbose_name='Récept. confirm')),
                ('external_expert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.CorpContact', verbose_name='Expert externe')),
                ('internal_expert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Expert interne')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stages.ExamEDESession', verbose_name='Session')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Student')),
                ('type_exam', models.CharField(choices=[('exam', 'Examen qualification'), ('entr', 'Entretien professionnel')], default='', max_length=10, verbose_name='Type')),
            ],
            options={
                'verbose_name': 'Examen',
            },
        ),
    ]
