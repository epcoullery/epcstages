from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0006_residence_permits_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='validation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Envoi mail de validation'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='convocation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Envoi mail de convocation'),
        ),
        migrations.RenameField(
            model_name='candidate',
            old_name='date_confirmation_mail',
            new_name='confirmation_date',
        ),
        migrations.AlterField(
            model_name='candidate',
            name='confirmation_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Envoi mail de confirmation'),
        ),
    ]
