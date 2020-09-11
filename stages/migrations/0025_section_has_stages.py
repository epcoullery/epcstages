from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0024_mark_fields_dup'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='has_stages',
            field=models.BooleanField(default=False, verbose_name='Planifie la PP sur ce site'),
        ),
        migrations.AlterField(
            model_name='period',
            name='section',
            field=models.ForeignKey(limit_choices_to={'has_stages': True}, on_delete=models.deletion.PROTECT, to='stages.Section', verbose_name='Filière'),
        ),
    ]
