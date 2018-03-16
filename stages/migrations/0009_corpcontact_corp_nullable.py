from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0008_add_logbook'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpcontact',
            name='corporation',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, to='stages.Corporation', verbose_name='Institution'),
        ),
    ]
