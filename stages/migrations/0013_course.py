from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0012_added_student_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('klass', models.CharField(default='', max_length=40, verbose_name='Classe(s)')),
                ('subject', models.CharField(default='', max_length=100, verbose_name='Sujet')),
                ('section', models.CharField(default='', max_length=10, verbose_name='Section')),
                ('period', models.IntegerField(default=0, verbose_name='Nb de périodes')),
                ('imputation', models.CharField(choices=[('ASAFE', 'ASAFE'), ('ASEFE', 'ASEFE'), ('ASSCFE', 'ASSCFE'), ('EDEpe', 'EDEpe'), ('EDEps', 'EDEps'), ('EDE', 'EDE'), ('EDS', 'EDS'), ('CAS-FPP', 'CAS-FPP')], max_length=10, verbose_name='Imputation')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='stages.Teacher', verbose_name="Enseignant-e")),
            ],
            options={
                'verbose_name': 'Cours',
                'verbose_name_plural': 'Cours',
            },
        ),
    ]
