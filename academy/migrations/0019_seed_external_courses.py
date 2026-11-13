from django.db import migrations


COURSES = [
    {
        'title': 'Objectif IA : initiez-vous à l’intelligence artificielle',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/6417031-objectif-ia-initiez-vous-a-l-intelligence-artificielle',
        'is_free': True,
        'description': 'Découvre les bases de l’intelligence artificielle, ses usages, ses opportunités et ses enjeux, puis explore les grandes étapes d’un projet d’IA.',
        'domain': 'Intelligence artificielle',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Fondamentaux de l’IA', 'Machine learning', 'Deep learning', 'IA responsable'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/6417031/6417031_teaser_picture_1739555053.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Maîtrisez les fondamentaux d’Excel',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/7168336-maitrisez-les-fondamentaux-d-excel',
        'is_free': True,
        'description': 'Apprends à créer et mettre en forme des tableaux, utiliser des formules, trier des données et construire des tableaux croisés dynamiques.',
        'domain': 'Bureautique et données',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Bases d’Excel', 'Formules', 'Tri et filtres', 'Tableaux croisés dynamiques'],
        'credential_info': 'Le cours prépare aux notions de base d’Excel ; l’éventuelle certification TOSA est distincte et non incluse dans le cours.',
        'cover_image_url': 'https://course.oc-static.com/courses/7168336/7168336_teaser_picture_1763563072.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Initiez-vous à Linux',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/7170491-initiez-vous-a-linux',
        'is_free': True,
        'description': 'Découvre le système Linux, installe un environnement et apprends à utiliser ses principales fonctions pour le travail et le développement.',
        'domain': 'Systèmes et réseaux',
        'level': 'Débutant',
        'duration': '8 heures',
        'language': 'Français',
        'skills': ['Découverte de Linux', 'Commandes de base', 'Environnement de travail'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/7170491/7170491_teaser_picture_1710272101.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Administrez un système Linux',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/7274161-administrez-un-systeme-linux',
        'is_free': True,
        'description': 'Apprends à administrer un serveur Linux : commandes et shell, gestion des fichiers, réseau et surveillance du système.',
        'domain': 'Administration système',
        'level': 'Intermédiaire',
        'duration': '10 heures',
        'language': 'Français',
        'skills': ['Terminal Linux', 'Shell Bash', 'Administration système', 'Réseaux'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/7274161/7274161_teaser_picture_1680859142.jpg',
        'provider_logo_url': '',
    },
]


def seed_external_courses(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias

    for course in COURSES:
        Formation.objects.using(database).update_or_create(
            link=course['link'],
            hosted_by_jupython=False,
            defaults=course,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0018_formation_course_visuals'),
    ]

    operations = [
        migrations.RunPython(seed_external_courses, migrations.RunPython.noop),
    ]
