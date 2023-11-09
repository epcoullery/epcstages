from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0036_corpcontact_etat_civil'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='start_educ',
            field=models.DateField(blank=True, null=True, verbose_name='Entrée en formation'),
        ),
    ]
