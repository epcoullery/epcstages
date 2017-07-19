from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0020_remove_old_ext_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klass',
            name='name',
            field=models.CharField(max_length=10, unique=True, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='student',
            name='klass',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.PROTECT, to='stages.Klass', verbose_name='Classe'),
        ),
    ]
