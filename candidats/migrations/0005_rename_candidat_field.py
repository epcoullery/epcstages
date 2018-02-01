from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0004_complement_ede_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='certif_800_general',
            new_name='certif_of_800_general',
        ),
    ]
