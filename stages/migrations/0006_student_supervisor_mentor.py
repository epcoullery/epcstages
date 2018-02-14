from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0005_extend_student_avs'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='mentor',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='rel_mentor', to='stages.CorpContact', verbose_name='Mentor'),
        ),
        migrations.AddField(
            model_name='student',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='rel_supervisor', to='stages.CorpContact', verbose_name='Superviseur'),
        ),
    ]
