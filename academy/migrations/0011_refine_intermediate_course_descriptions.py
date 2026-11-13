from django.db import migrations


DESCRIPTIONS = {
    'Développer une API professionnelle avec Django REST': (
        'Conçois une API REST avec Django, authentification, permissions par utilisateur, tests automatisés et '
        'documentation prête pour une mise en production.'
    ),
    'Cybersécurité défensive : analyser et répondre aux incidents': (
        'Apprends à trier des alertes, lire des journaux et rédiger un plan de réponse défensive à partir de scénarios '
        'autorisés et de données fictives.'
    ),
    'Data Analytics : transformer un jeu de données en décision': (
        'Nettoie et analyse des données avec Python, Pandas et SQL, puis transforme des résultats contrôlés en '
        'recommandations claires.'
    ),
    'DevOps : automatiser les tests et livrer une application': (
        'Automatise les tests, prépare une application conteneurisée et définis un processus de livraison, de '
        'surveillance et de retour arrière.'
    ),
}


def refine_course_descriptions(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias
    for title, description in DESCRIPTIONS.items():
        Formation.objects.using(database).filter(
            title=title,
            platform='Jupython',
        ).update(description=description)


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0010_seed_intermediate_learning_paths'),
    ]

    operations = [
        migrations.RunPython(refine_course_descriptions, migrations.RunPython.noop),
    ]
