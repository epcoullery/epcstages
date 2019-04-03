from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0020_teacher_to_user_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='can_examinate',
            field=models.BooleanField(default=False, verbose_name='Peut corriger examens candidats'),
        ),
    ]
