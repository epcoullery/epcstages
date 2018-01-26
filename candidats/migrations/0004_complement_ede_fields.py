# Generated by Django 2.0 on 2018-01-26 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidats', '0003_add_interview_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='certif_of_800h',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='certif_of_cfc',
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='proc_admin_ext',
        ),
        migrations.AddField(
            model_name='candidate',
            name='activity_rate',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name="Taux d'activité"),
        ),
        migrations.AddField(
            model_name='candidate',
            name='aes_accords',
            field=models.PositiveSmallIntegerField(choices=[(0, 'OK'), (1, 'Demander accord du canton concerné'), (2, 'Refus du canton concerné')], default=0, verbose_name='Accord AES'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='certif_800_general',
            field=models.BooleanField(default=False, verbose_name='Attest. 800h. général'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='certif_of_800_childhood',
            field=models.BooleanField(default=False, verbose_name='Attest. 800h. enfance'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='convocation_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='diploma',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Aucun'), (1, "CFC d'ASE"), (2, 'CFC autre domaine'), (3, 'Matu acad./spéc. ou dipl. ECG'), (4, 'Portfolio')], default=0, verbose_name='Titre sec. II'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='diploma_detail',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='Détail titre'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='diploma_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Inconnu'), (1, 'En cours'), (2, 'OK')], default=0, verbose_name='Statut titre'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='inscr_other_school',
            field=models.CharField(default='', max_length=30, verbose_name='Inscr. autre école'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='residence_permits',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Pas nécessaire'), (1, 'Nécessaire - OK'), (2, 'Manquante')], default=0, verbose_name='Autorisation de séjour (pour les personnes étrangères)'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='option',
            field=models.CharField(blank=True, choices=[('GEN', 'Généraliste'), ('ENF', 'Enfance'), ('PAG', 'Personnes âgées'), ('HAN', 'Handicap'), ('PE-5400h', 'Parcours Emploi 5400h.'), ('PE-3600h', 'Parcours Emploi 3600h.'), ('PS', 'Parcours stage 5400h.')], max_length=20, verbose_name='Option'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='work_certificate',
            field=models.BooleanField(default=False, verbose_name='Bilan act. prof./dernier stage'),
        ),
    ]
