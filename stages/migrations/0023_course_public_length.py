from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0022_corporation_unique_name_and_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='public',
            field=models.CharField(default='', max_length=100, verbose_name='Classe(s)'),
        ),
    ]
