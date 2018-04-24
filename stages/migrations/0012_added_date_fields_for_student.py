from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0011_complement_corpcontact_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='date_confirm_received',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Récept. confirm'),
        ),
        migrations.AddField(
            model_name='student',
            name='date_soutenance_mailed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Convoc. env.'),
        ),
    ]
