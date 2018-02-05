from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '__first__'),
        ('candidats', '0002_deposit_date_non_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('room', models.CharField(max_length=20, verbose_name="Salle d'entretien")),
                ('status', models.CharField(choices=[('N', 'Normal'), ('R', 'Réserve'), ('X', 'Attente confirmation enseignants')], default='N', max_length=1, verbose_name='Statut')),
            ],
            options={
                'ordering': ('date',),
                'verbose_name': "Entretien d'admission",
                'verbose_name_plural': "Entretiens d'admission",
            },
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='file_resp',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='interview_date',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='interview_resp',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='interview_room',
        ),
        migrations.AddField(
            model_name='interview',
            name='candidat',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='candidats.Candidate'),
        ),
        migrations.AddField(
            model_name='interview',
            name='teacher_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Ens. dossier'),
        ),
        migrations.AddField(
            model_name='interview',
            name='teacher_int',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Ens. entretien'),
        ),
    ]
