from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0030_add_contact_avs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corpcontact',
            name='ccp',
        ),
    ]
