from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0012_model_adapts_dec_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='session',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2024, 'Année 2024'), (2025, 'Année 2025'), (2026, 'Année 2026')], null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='option',
            field=models.CharField(blank=True, choices=[('GEN', 'Généraliste'), ('ENF', 'Enfance'), ('PAG', 'Personnes âgées'), ('HAN', 'Handicap'), ('PE-5400h', 'Voie duale 5400h.'), ('PE-3600h', 'Voie duale 3600h.'), ('PS-3600h', 'Voie stages intégrés 3600h.'), ('PS', 'Voie stages intégrés 5400h.')], max_length=20, verbose_name='Option'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='section',
            field=models.CharField(choices=[('ASA', 'Aide en soin et accompagnement AFP'), ('ASE', 'Assist. socio-éducatif-ve CFC'), ('ASSC', 'Assist. en soin et santé communautaire CFC'), ('EDE', 'Education de l’enfance, dipl. ES'), ('EDS', 'Education sociale, dipl. ES'), ('MSP', 'Maitrise socioprofessionnelle, dipl. ES')], max_length=10, verbose_name='Filière'),
        ),
    ]
