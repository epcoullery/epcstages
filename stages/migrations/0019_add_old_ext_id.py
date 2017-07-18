from django.db import migrations, models


def migrate_extid(apps, schema_editor):
    Corporation = apps.get_model("stages", "Corporation")
    CorpContact = apps.get_model("stages", "CorpContact")
    Corporation.objects.update(ext_id_old=models.F('ext_id'))
    CorpContact.objects.update(ext_id_old=models.F('ext_id'))
    Corporation.objects.update(ext_id=None)
    CorpContact.objects.update(ext_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0018_removed_referent_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpcontact',
            name='ext_id_old',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (ancien)'),
        ),
        migrations.AddField(
            model_name='corporation',
            name='ext_id_old',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID externe (ancien)'),
        ),
        migrations.RunPython(migrate_extid, migrations.RunPython.noop),
    ]
