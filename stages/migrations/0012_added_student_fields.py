from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0011_add_teacher_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporation',
            name='district',
            field=models.CharField(blank=True, max_length=20, verbose_name='Canton'),
        ),
        migrations.AddField(
            model_name='student',
            name='avs',
            field=models.CharField(blank=True, max_length=15, verbose_name='No AVS'),
        ),
        migrations.AddField(
            model_name='student',
            name='corporation',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='stages.Corporation', verbose_name='Employeur'),
        ),
        migrations.AddField(
            model_name='student',
            name='dispense_ecg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='dispense_eps',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='district',
            field=models.CharField(blank=True, max_length=20, verbose_name='Canton'),
        ),
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.CharField(blank=True, max_length=3, verbose_name='Genre'),
        ),
        migrations.AddField(
            model_name='student',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='stages.CorpContact', verbose_name='FEE/FPP'),
        ),
        migrations.AddField(
            model_name='student',
            name='soutien_dys',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='student',
            name='birth_date',
            field=models.DateField(blank=True, verbose_name='Date de naissance'),
        ),
    ]
