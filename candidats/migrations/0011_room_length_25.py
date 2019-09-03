from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0010_Added convoc_confirm_receipt_on_Candidate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='room',
            field=models.CharField(max_length=25, verbose_name="Salle d'entretien"),
        ),
    ]
