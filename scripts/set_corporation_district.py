import sys, os, django
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.settings")
django.setup()

from stages.models import Corporation

for corp in Corporation.objects.all():
    # PCode for neuchâtel district
    if corp.district == '':
        pcode = int(corp.pcode)
        if pcode in range(2000,2334) or pcode in range(2400, 2417) or pcode in [2523, 2525, 2616]:
            corp.district = 'NE'
            corp.save()
        if pcode in range(2336,2365) or pcode in range(2714, 2719) or pcode in range(2800,2955):
            corp.district = 'JU'
            corp.save()
        if pcode in [2333, 2346] or pcode in range(2500, 2521) or pcode in range(2532,2763) or pcode in range(3000,3865):
            corp.district = 'BE'
            corp.save()



