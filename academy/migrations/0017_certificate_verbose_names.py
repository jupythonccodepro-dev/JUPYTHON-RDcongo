# Generated minimal migration to add verbose_name/help_text metadata for Certificate
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0016_clarify_certificate_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='certificate_url',
            field=models.URLField(
                verbose_name='Lien du justificatif (URL HTTPS)',
                help_text='Lien HTTPS vers un justificatif émis par le fournisseur de la formation.',
            ),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='verified',
            field=models.BooleanField(
                verbose_name='Justificatif examiné par Jupython',
                default=False,
                help_text=('Indique que Jupython a examiné le justificatif soumis. '
                           "Cela n’implique pas une validation de l’émetteur : seul l’organisme ayant délivré le document peut confirmer son authenticité."),
            ),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='issued_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Date d’émission'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='verified_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Date d’examen'),
        ),
        migrations.AlterModelOptions(
            name='certificate',
            options={'ordering': ['-issued_at', '-verified_at'], 'verbose_name': 'Justificatif', 'verbose_name_plural': 'Justificatifs'},
        ),
    ]
