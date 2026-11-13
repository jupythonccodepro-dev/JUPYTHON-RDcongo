# Généré par Django 6.0 le 2026-09-29 à 20:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0012_refine_capstone_labels'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleQuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('choices', models.JSONField(default=list)),
                ('correct_choice', models.PositiveSmallIntegerField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_questions', to='academy.coursemodule')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ModuleQuizProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('best_score', models.PositiveSmallIntegerField(default=0)),
                ('passed', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_progress', to='academy.coursemodule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_quiz_progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'module'), name='unique_user_module_quiz_progress')],
            },
        ),
    ]
