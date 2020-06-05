from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0031_remove_contact_ccp'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='nation',
            field=models.CharField(blank=True, max_length=40, verbose_name='Nationalité'),
        ),
    ]
