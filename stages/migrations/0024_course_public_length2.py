from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0023_course_public_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='public',
            field=models.CharField(default='', max_length=200, verbose_name='Classe(s)'),
        ),
    ]
