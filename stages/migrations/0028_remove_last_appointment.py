from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0027_migrate_exams'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='last_appointment',
        ),
        migrations.AlterField(
            model_name='examination',
            name='type_exam',
            field=models.CharField(choices=[('exam', 'Examen qualification'), ('entr', 'Entretien professionnel')], max_length=10, verbose_name='Type'),
        ),
    ]
