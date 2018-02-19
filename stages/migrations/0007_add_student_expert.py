from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0006_student_supervisor_mentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='expert',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='rel_expert', to='stages.CorpContact', verbose_name='Expert'),
        ),
    ]
