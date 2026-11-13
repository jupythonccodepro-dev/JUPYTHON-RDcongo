from django.db import migrations


COURSES = [
    {
        'title': 'Créez votre site web avec HTML5 et CSS3',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/1603881-creez-votre-site-web-avec-html5-et-css3',
        'is_free': True,
        'description': 'Apprends à structurer une page web en HTML, à la mettre en forme en CSS, puis à organiser une mise en page responsive.',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '15 heures',
        'language': 'Français',
        'skills': ['HTML5', 'CSS3', 'Flexbox', 'CSS Grid', 'Responsive design'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/1603881/1603881_teaser_picture_1780557361.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Apprenez à programmer avec JavaScript',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/7696886-apprenez-a-programmer-avec-javascript',
        'is_free': True,
        'description': 'Découvre les bases de JavaScript en manipulant des données et en créant des interactions et formulaires pour un site web.',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '12 heures',
        'language': 'Français',
        'skills': ['JavaScript', 'Logique de programmation', 'DOM', 'Formulaires web'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/7696886/7696886_teaser_picture_1739555145.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Implémentez vos bases de données relationnelles avec SQL',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/6971126-implementez-vos-bases-de-donnees-relationnelles-avec-sql',
        'is_free': True,
        'description': 'Apprends à créer une base MySQL, manipuler les données avec les opérations CRUD et écrire des requêtes SQL avancées.',
        'domain': 'Données et bases de données',
        'level': 'Intermédiaire',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['SQL', 'MySQL', 'Requêtes CRUD', 'Modélisation relationnelle'],
        'credential_info': 'Cours en libre accès. Un niveau de base en modélisation de données est recommandé ; aucune certification incluse n’est annoncée.',
        'cover_image_url': 'https://course.oc-static.com/courses/6971126/6971126_teaser_picture_1737642993.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Gérez du code avec Git et GitHub',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/7162856-gerez-du-code-avec-git-et-github',
        'is_free': True,
        'description': 'Installe et configure Git et GitHub, suis les changements de ton code avec les commandes de base et corrige les erreurs courantes.',
        'domain': 'Développement logiciel',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Git', 'GitHub', 'Contrôle de versions', 'Branches'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/7162856/7162856_teaser_picture_1708722376.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Apprenez à utiliser la ligne de commande dans un terminal',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/6173491-apprenez-a-utiliser-la-ligne-de-commande-dans-un-terminal',
        'is_free': True,
        'description': 'Découvre le terminal, apprends à lancer des commandes et à naviguer dans les dossiers et fichiers de ton ordinateur.',
        'domain': 'Systèmes et outils développeur',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Terminal', 'Ligne de commande', 'Gestion de fichiers'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/6173491/6173491_teaser_picture_1706083893.jpg',
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
        ('academy', '0019_seed_external_courses'),
    ]

    operations = [
        migrations.RunPython(seed_external_courses, migrations.RunPython.noop),
    ]
