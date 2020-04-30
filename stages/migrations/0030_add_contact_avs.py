from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0029_delete_exam_fields_on_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='avs',
            field=models.CharField(blank=True, max_length=20, verbose_name='No AVS'),
        ),
    ]
