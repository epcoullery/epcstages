from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0014_added_supervisionbill_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='supervision_attest_received',
            field=models.BooleanField(default=False, verbose_name='Attest. supervision reçue'),
        ),
    ]
