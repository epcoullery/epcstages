from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0012_added_date_fields_for_student'),
    ]

    operations = [
        migrations.RenameField(
            model_name='corpcontact',
            old_name='title',
            new_name='civility',
        ),
    ]
