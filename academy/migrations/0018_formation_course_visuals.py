from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0017_certificate_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='formation',
            name='cover_image',
            field=models.ImageField(
                blank=True,
                help_text='Visuel cr?? ou fourni par Jupython, pour les cours internes.',
                upload_to='academy/course-covers/',
            ),
        ),
        migrations.AddField(
            model_name='formation',
            name='cover_image_url',
            field=models.URLField(
                blank=True,
                help_text='URL HTTPS du visuel officiel du cours externe, provenant du site fournisseur.',
            ),
        ),
        migrations.AddField(
            model_name='formation',
            name='provider_logo_url',
            field=models.URLField(
                blank=True,
                help_text='URL HTTPS du logo officiel du fournisseur externe.',
            ),
        ),
    ]
