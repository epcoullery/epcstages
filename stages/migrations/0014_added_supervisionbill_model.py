from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0013_renamed_title_to_civility'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupervisionBill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.SmallIntegerField(default=0, verbose_name='période')),
                ('date', models.DateField()),
                ('student', models.ForeignKey(on_delete=models.deletion.CASCADE, to='stages.Student', verbose_name='étudiant')),
                ('supervisor', models.ForeignKey(on_delete=models.deletion.CASCADE, to='stages.CorpContact', verbose_name='superviseur')),
            ],
            options={
                'ordering': ['date'],
                'verbose_name': 'Facture de supervision',
                'verbose_name_plural': 'Factures de supervision',
            },
        ),
    ]
