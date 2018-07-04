from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0016_populate_corp_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='login_rpn',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
