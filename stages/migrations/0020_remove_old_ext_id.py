from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0019_add_old_ext_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corpcontact',
            name='ext_id_old',
        ),
        migrations.RemoveField(
            model_name='corporation',
            name='ext_id_old',
        ),
    ]
