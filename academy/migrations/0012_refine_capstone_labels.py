from django.db import migrations


def refine_capstone_labels(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias
    for formation in Formation.objects.using(database).filter(
        platform='Jupython',
        hosted_by_jupython=True,
        project_outcome__startswith='Projet final : ',
    ):
        formation.project_outcome = formation.project_outcome.removeprefix('Projet final : ')
        formation.save(update_fields=['project_outcome'])


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0011_refine_intermediate_course_descriptions'),
    ]

    operations = [
        migrations.RunPython(refine_capstone_labels, migrations.RunPython.noop),
    ]
