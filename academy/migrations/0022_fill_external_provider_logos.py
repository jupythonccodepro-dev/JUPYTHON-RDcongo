from django.db import migrations


PROVIDER_LOGOS = {
    'OpenClassrooms': 'https://openclassrooms.com/favicon.ico',
    'Cisco Networking Academy': 'https://www.netacad.com/favicon.ico',
    'IBM SkillsBuild': 'https://skillsbuild.org/favicon.ico',
    'Microsoft Learn': 'https://learn.microsoft.com/favicon.ico',
    'MDN Web Docs': 'https://developer.mozilla.org/favicon.ico',
}


def fill_provider_logos(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias

    for platform, logo_url in PROVIDER_LOGOS.items():
        Formation.objects.using(database).filter(
            hosted_by_jupython=False,
            platform=platform,
            provider_logo_url='',
        ).update(provider_logo_url=logo_url)


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0021_external_ai_courses'),
    ]

    operations = [
        migrations.RunPython(fill_provider_logos, migrations.RunPython.noop),
    ]
