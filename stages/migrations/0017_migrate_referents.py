from django.db import migrations


def migrate_referents(apps, schema_editor):
    Teacher = apps.get_model("stages", "Teacher")
    Training = apps.get_model("stages", "Training")
    errors = False
    for tr in Training.objects.filter(referent_old__isnull=False):
        if tr.referent_old.last_name == 'Liechti Held':
            last_name = 'Liechti'
        elif tr.referent_old.last_name == 'Haldimann Luethi':
            last_name = 'Haldimann'
        elif tr.referent_old.last_name == 'Kummer':
            last_name = 'Kummer-Invernizzi'
        else:
            last_name = tr.referent_old.last_name
        try:
            tr.referent = Teacher.objects.get(first_name=tr.referent_old.first_name.strip(), last_name=last_name)
        except Teacher.DoesNotExist:
            print("Unable to find referent %s in teachers" % " ".join([tr.referent_old.first_name, tr.referent_old.last_name]))
        else:
            tr.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0016_referent_to_teacher'),
    ]

    operations = [migrations.RunPython(migrate_referents, migrations.RunPython.noop),]
