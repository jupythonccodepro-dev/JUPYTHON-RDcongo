# Généré par Django 6.0 le 2026-09-29 à 17:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0004_refine_course_metadata'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='formation',
            name='hosted_by_jupython',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='formation',
            name='last_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='CourseModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='academy.formation')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='CourseLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('exercise', models.TextField(blank=True)),
                ('learning_objectives', models.JSONField(blank=True, default=list)),
                ('duration_minutes', models.PositiveIntegerField(default=15)),
                ('order', models.PositiveIntegerField(default=0)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='academy.coursemodule')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='academy.courselesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['completed_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='coursemodule',
            constraint=models.UniqueConstraint(fields=('formation', 'order'), name='unique_course_module_order'),
        ),
        migrations.AddConstraint(
            model_name='courselesson',
            constraint=models.UniqueConstraint(fields=('module', 'order'), name='unique_module_lesson_order'),
        ),
        migrations.AddConstraint(
            model_name='lessonprogress',
            constraint=models.UniqueConstraint(fields=('user', 'lesson'), name='unique_user_lesson_progress'),
        ),
    ]
