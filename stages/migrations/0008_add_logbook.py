from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0007_add_student_expert'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_date', models.DateField(auto_now_add=True, verbose_name='Date de saisie')),
                ('start_date', models.DateField(verbose_name='Date de début')),
                ('end_date', models.DateField(verbose_name='Date de fin')),
                ('nb_period', models.IntegerField(verbose_name='Périodes')),
                ('comment', models.CharField(blank=True, max_length=200, verbose_name='Commentaire motif')),
            ],
            options={
                'verbose_name': 'Carnet du lait',
                'verbose_name_plural': 'Carnets du lait',
            },
        ),
        migrations.CreateModel(
            name='LogBookReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Motif')),
            ],
            options={
                'verbose_name': 'Motif de carnet du lait',
                'verbose_name_plural': 'Motifs de carnet du lait',
            },
        ),
        migrations.AddField(
            model_name='logbook',
            name='reason',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stages.LogBookReason', verbose_name='Catégorie de motif'),
        ),
        migrations.AddField(
            model_name='logbook',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stages.Teacher', verbose_name='Enseignant'),
        ),
    ]
