from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_user_avatar_user_bio_user_public_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='promotion',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
