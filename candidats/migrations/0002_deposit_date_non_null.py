from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='deposite_date',
            field=models.DateField(verbose_name='Date dépôt dossier'),
        ),
    ]
