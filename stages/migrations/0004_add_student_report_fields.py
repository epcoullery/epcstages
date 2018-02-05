from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0003_student_birthdate_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='report_sem1',
            field=models.FileField(blank=True, null=True, upload_to='bulletins', verbose_name='Bulletin 1er sem.'),
        ),
        migrations.AddField(
            model_name='student',
            name='report_sem1_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date envoi bull. sem 1'),
        ),
        migrations.AddField(
            model_name='student',
            name='report_sem2',
            field=models.FileField(blank=True, null=True, upload_to='bulletins', verbose_name='Bulletin 2e sem.'),
        ),
        migrations.AddField(
            model_name='student',
            name='report_sem2_sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date envoi bull. sem 2'),
        ),
    ]
