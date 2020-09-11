from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0033_room_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='instructor2',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='rel_instructor2', to='stages.CorpContact', verbose_name='FEE/FPP (2)'),
        ),
    ]
