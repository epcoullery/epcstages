# Generated by Django 2.0.1 on 2018-04-26 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0013_renamed_title_to_civility'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='supervision_attest_received',
            field=models.BooleanField(default=False, verbose_name='attest. supervision reçue'),
        ),
    ]
