from django.db import migrations


def refine_course_metadata(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias
    metadata = {
        'Python Essentials 1': ['Bases de Python'],
        'Notions de base sur la mise en réseau': ['Bases des réseaux informatiques'],
        'Python Essentials 2': ['Python niveau suivant'],
    }

    for title, skills in metadata.items():
        Formation.objects.using(database).filter(
            title=title,
            platform='Cisco Networking Academy',
        ).update(skills=skills)


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0003_enrollment_status_formation_credential_info_and_more'),
    ]

    operations = [
        migrations.RunPython(refine_course_metadata, migrations.RunPython.noop),
    ]
