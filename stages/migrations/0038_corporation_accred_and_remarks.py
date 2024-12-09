from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0037_student_start_educ'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporation',
            name='accred',
            field=models.BooleanField(default=False, verbose_name='Accréditation'),
        ),
        migrations.AddField(
            model_name='corporation',
            name='accred_from',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028')], null=True, verbose_name='Depuis'),
        ),
        migrations.AddField(
            model_name='corporation',
            name='remarks',
            field=models.TextField(blank=True, verbose_name='Remarques'),
        ),
    ]
