from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0013_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de naissance'),
        ),
    ]
