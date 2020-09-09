from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0032_contact_nationalite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examination',
            name='room',
            field=models.CharField(blank=True, max_length=30, verbose_name='Salle'),
        ),
    ]
