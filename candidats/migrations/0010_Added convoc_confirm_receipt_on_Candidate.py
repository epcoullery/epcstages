from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0009_remove_total_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='convoc_confirm_receipt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Accusé de réception'),
        ),
    ]
