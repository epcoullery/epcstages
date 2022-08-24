from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0035_contact_permis_sejour'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='etat_civil',
            field=models.CharField(blank=True, max_length=20, verbose_name='État-civil'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='etat_depuis',
            field=models.DateField(blank=True, null=True, verbose_name='Depuis le'),
        ),
    ]
