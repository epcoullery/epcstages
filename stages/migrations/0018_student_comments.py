from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0017_add_login_field_for_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.ForeignKey(on_delete=models.deletion.CASCADE, to='stages.Student')),
                ('fichier', models.FileField(upload_to='etudiants')),
                ('titre', models.CharField(max_length=200, verbose_name='Titre')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='mc_comment',
            field=models.TextField(blank=True, verbose_name='Commentaires'),
        ),
    ]
