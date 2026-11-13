from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0022_fill_external_provider_logos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonPracticeSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.TextField(verbose_name='R?ponse ou lien vers le travail')),
                ('status', models.CharField(choices=[('pending', '? corriger'), ('revision', '? refaire'), ('approved', 'Valid?e')], default='pending', max_length=12)),
                ('feedback', models.TextField(blank=True, verbose_name='Retour au participant')),
                ('submitted_at', models.DateTimeField(auto_now=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practice_submissions', to='academy.courselesson')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_practice_submissions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_practice_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Remise de pratique', 'verbose_name_plural': 'Remises de pratique', 'ordering': ['status', 'submitted_at']},
        ),
        migrations.AddConstraint(
            model_name='lessonpracticesubmission',
            constraint=models.UniqueConstraint(fields=('user', 'lesson'), name='unique_user_lesson_practice_submission'),
        ),
    ]
