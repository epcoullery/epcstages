from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0011_room_length_25'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='certif_of_800_childhood',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='marks_certificate',
        ),
        migrations.RenameField(
            model_name='candidate',
            old_name='certif_of_800_general',
            new_name='certif_of_400_general',
        ),
        migrations.AlterField(
            model_name='candidate',
            name='certif_of_400_general',
            field=models.BooleanField(default=False, verbose_name='Attest. 400h. général'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='work_certificate',
            field=models.BooleanField(default=False, verbose_name='Préavis formatif'),
        ),
    ]
