from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0028_remove_last_appointment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examedesession',
            options={'ordering': ['-year', 'season'], 'verbose_name': 'Session d’examen'},
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_confirm_ep_received',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_confirm_received',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_exam',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_exam_ep',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_soutenance_ep_mailed',
        ),
        migrations.RemoveField(
            model_name='student',
            name='date_soutenance_mailed',
        ),
        migrations.RemoveField(
            model_name='student',
            name='expert_ep',
        ),
        migrations.RemoveField(
            model_name='student',
            name='internal_expert',
        ),
        migrations.RemoveField(
            model_name='student',
            name='internal_expert_ep',
        ),
        migrations.RemoveField(
            model_name='student',
            name='mark',
        ),
        migrations.RemoveField(
            model_name='student',
            name='mark_acq',
        ),
        migrations.RemoveField(
            model_name='student',
            name='mark_ep',
        ),
        migrations.RemoveField(
            model_name='student',
            name='mark_ep_acq',
        ),
        migrations.RemoveField(
            model_name='student',
            name='room',
        ),
        migrations.RemoveField(
            model_name='student',
            name='room_ep',
        ),
        migrations.RemoveField(
            model_name='student',
            name='session',
        ),
        migrations.RemoveField(
            model_name='student',
            name='session_ep',
        ),
    ]
