from django.db import migrations


def populate_district(apps, schema_editor):
    Corporation = apps.get_model('stages', 'Corporation')

    for corp in Corporation.objects.filter(district=''):
        pcode = int(corp.pcode)
        if pcode in range(2000, 2334) or pcode in range(2400, 2417) or pcode in [2523, 2525, 2616]:
            corp.district = 'NE'
            corp.save()
        elif pcode in range(2336, 2365) or pcode in range(2714, 2719) or pcode in range(2800, 2955):
            corp.district = 'JU'
            corp.save()
        elif pcode in [2333, 2346] or pcode in range(2500, 2521) or pcode in range(2532, 2763) or pcode in range(3000, 3865):
            corp.district = 'BE'
            corp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0015_added_supervision_attest_field'),
    ]

    operations = [migrations.RunPython(populate_district)]
