from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0004_add_student_report_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='avs',
            field=models.CharField(blank=True, max_length=20, verbose_name='No AVS'),
        ),
    ]
