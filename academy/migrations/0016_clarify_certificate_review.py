from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0015_guided_intermediate_practice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='certificate_url',
            field=models.URLField(
                help_text='Lien HTTPS vers un certificat émis par le fournisseur de la formation.',
            ),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='verified',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Indique que Jupython a examiné le justificatif soumis. '
                    'Ne confirme pas son authenticité auprès de l’organisme émetteur.'
                ),
            ),
        ),
    ]
