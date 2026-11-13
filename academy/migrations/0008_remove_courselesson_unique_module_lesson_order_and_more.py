# Généré par Django 6.0 le 2026-09-29 à 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0007_add_verified_provider_courses'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='courselesson',
            name='unique_module_lesson_order',
        ),
        migrations.RemoveConstraint(
            model_name='coursemodule',
            name='unique_course_module_order',
        ),
    ]
