# Généré par Django 6.0 le 2026-09-29 à 12:32

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academy',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='certificate',
            options={'ordering': ['-issued_at', '-verified_at']},
        ),
        migrations.AlterModelOptions(
            name='enrollment',
            options={'ordering': ['-date_joined']},
        ),
        migrations.AlterModelOptions(
            name='formation',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='formation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formation',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddConstraint(
            model_name='certificate',
            constraint=models.UniqueConstraint(fields=('user', 'formation'), name='unique_user_formation_certificate'),
        ),
        migrations.AddConstraint(
            model_name='enrollment',
            constraint=models.UniqueConstraint(fields=('user', 'formation'), name='unique_user_formation_enrollment'),
        ),
    ]
