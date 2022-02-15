from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0034_add_instructor2'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='date_validite',
            field=models.DateField(blank=True, null=True, verbose_name='Date de validité'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='permis_sejour',
            field=models.CharField(blank=True, max_length=15, verbose_name='Permis de séjour'),
        ),
    ]
