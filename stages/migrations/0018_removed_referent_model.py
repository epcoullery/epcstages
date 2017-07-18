from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0017_migrate_referents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='referent_old',
        ),
        migrations.DeleteModel(
            name='Referent',
        ),
    ]
