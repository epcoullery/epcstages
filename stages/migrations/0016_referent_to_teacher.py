from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0015_auto_20170717_1515'),
    ]

    operations = [
        migrations.RenameField(
            model_name='training',
            old_name='referent',
            new_name='referent_old',
        ),
        migrations.AddField(
            model_name='training',
            name='referent',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='stages.Teacher', verbose_name='Référent'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
