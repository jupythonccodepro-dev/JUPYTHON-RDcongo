# Généré par Django 6.0 le 2026-09-29 à 16:22

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=accounts.models.avatar_upload_path),
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=280),
        ),
        migrations.AddField(
            model_name='user',
            name='public_name',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]
