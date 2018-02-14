from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '__first__'),
        ('candidats', '0007_candidate_datetime_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candidate',
            options={'ordering': ('last_name',), 'verbose_name': 'Candidat'},
        ),
        migrations.AddField(
            model_name='candidate',
            name='examination_teacher',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('abrev', 'MME'), ('abrev', 'CLG'), _connector='OR'), null=True, on_delete=models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Correct. dossier'),
        ),
    ]
