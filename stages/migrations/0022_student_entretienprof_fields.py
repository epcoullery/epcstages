from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0021_teacher_can_examinate'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='date_confirm_ep_received',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Récept. confirm'),
        ),
        migrations.AddField(
            model_name='student',
            name='date_exam_ep',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date exam. EP'),
        ),
        migrations.AddField(
            model_name='student',
            name='date_soutenance_ep_mailed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Convoc. env.'),
        ),
        migrations.AddField(
            model_name='student',
            name='expert_ep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rel_expert_ep', to='stages.CorpContact', verbose_name='Expert externe EP'),
        ),
        migrations.AddField(
            model_name='student',
            name='internal_expert_ep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rel_internal_expert_ep', to='stages.Teacher', verbose_name='Expert interne EP'),
        ),
        migrations.AddField(
            model_name='student',
            name='mark_ep',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Note EP'),
        ),
        migrations.AddField(
            model_name='student',
            name='room_ep',
            field=models.CharField(blank=True, max_length=15, verbose_name='Salle EP'),
        ),
        migrations.AddField(
            model_name='student',
            name='session_ep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_ep', to='stages.ExamEDESession', verbose_name='Session EP'),
        ),
        migrations.AlterField(
            model_name='student',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_es', to='stages.ExamEDESession'),
        ),
    ]
