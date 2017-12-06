from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0002_add_student_option_ase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de naissance'),
        ),
    ]
