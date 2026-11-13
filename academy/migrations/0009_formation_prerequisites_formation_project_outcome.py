# Généré par Django 6.0 le 2026-09-29 à 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0008_remove_courselesson_unique_module_lesson_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formation',
            name='prerequisites',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='project_outcome',
            field=models.TextField(blank=True),
        ),
    ]
