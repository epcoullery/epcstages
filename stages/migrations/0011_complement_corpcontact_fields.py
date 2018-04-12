from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0010_add_fields_for_examEDEsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='bank',
            field=models.CharField(blank=True, max_length=200, verbose_name='Banque (nom et ville)'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de naissance'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='ccp',
            field=models.CharField(blank=True, max_length=15, verbose_name='Compte de chèque postal'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='city',
            field=models.CharField(blank=True, max_length=40, verbose_name='Localité'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='clearing',
            field=models.CharField(blank=True, max_length=5, verbose_name='No clearing'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='fields_of_interest',
            field=models.TextField(blank=True, verbose_name='Domaines d’intérêts'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='iban',
            field=models.CharField(blank=True, max_length=21, verbose_name='iban'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='pcode',
            field=models.CharField(blank=True, max_length=4, verbose_name='Code postal'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='qualification',
            field=models.TextField(blank=True, verbose_name='Titres obtenus'),
        ),
        migrations.AddField(
            model_name='corpcontact',
            name='street',
            field=models.CharField(blank=True, max_length=100, verbose_name='Rue'),
        ),
    ]
