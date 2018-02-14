from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0008_add_examination_teacher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='total_result_mark',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='total_result_points',
        ),
    ]
