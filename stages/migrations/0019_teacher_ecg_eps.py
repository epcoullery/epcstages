from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0018_student_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='klass',
            name='teacher_ecg',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Maître ECG'),
        ),
        migrations.AddField(
            model_name='klass',
            name='teacher_eps',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='+', to='stages.Teacher', verbose_name='Maître EPS'),
        ),
    ]
