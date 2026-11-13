from django.db import migrations
from django.utils import timezone


COURSES = [
    {
        'title': 'Sensibilisation au numérique',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/digital-awareness?courseLang=fr-FR',
        'domain': 'Compétences numériques',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['Culture numérique', 'Sécurité numérique'],
        'description': 'Parcours gratuit et autonome pour acquérir les bases de la culture numérique.',
        'credential_info': 'Ce cours fait partie d’une série de quatre cours préparant à la certification OpenEDG Digital Literacy. L’examen et ses conditions sont distincts et restent à vérifier.',
    },
    {
        'title': 'Les bases du matériel informatique',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/computer-hardware-basics?courseLang=fr-FR',
        'domain': 'Informatique',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Composants informatiques', 'Matériel', 'Dépannage de base'],
        'description': 'Découvre les principaux composants d’un ordinateur et les bases du matériel informatique.',
        'credential_info': 'Cisco indique des badges de cours et de modules. Aucune certification professionnelle n’est incluse.',
    },
    {
        'title': 'Operating Systems Basics',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/operating-systems-basics?courseLang=en-US',
        'domain': 'Informatique',
        'level': 'Débutant',
        'duration': '12 heures',
        'language': 'Anglais',
        'skills': ['Systèmes d’exploitation', 'Gestion de fichiers'],
        'description': 'Cours autonome pour comprendre les bases et le rôle des systèmes d’exploitation.',
        'credential_info': 'Cisco indique un badge de cours et des badges de modules. Aucune certification professionnelle n’est incluse.',
    },
    {
        'title': 'JavaScript Essentials 1',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/javascript-essentials-1?courseLang=en-US',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '',
        'language': 'Anglais',
        'skills': ['JavaScript', 'Programmation web'],
        'description': 'Apprends les bases de JavaScript dans un cours autonome de Cisco Networking Academy.',
        'credential_info': 'Le cours inclut des badges de cours et de modules et prépare au parcours JSE. L’examen de certification JSE est distinct et non inclus.',
    },
    {
        'title': 'Décrire les concepts du cloud',
        'platform': 'Microsoft Learn',
        'link': 'https://learn.microsoft.com/fr-fr/training/paths/microsoft-azure-fundamentals-describe-cloud-concepts/',
        'domain': 'Cloud',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['Informatique en nuage', 'Modèles cloud', 'Services Azure'],
        'description': 'Parcours Microsoft Learn en trois modules pour découvrir les concepts du cloud.',
        'credential_info': 'Progression et réussite du parcours dans Microsoft Learn. Ce parcours ne vaut pas une certification AZ-900.',
    },
    {
        'title': 'Décrire l’architecture et les services Azure',
        'platform': 'Microsoft Learn',
        'link': 'https://learn.microsoft.com/fr-fr/training/paths/azure-fundamentals-describe-azure-architecture-services/',
        'domain': 'Cloud',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['Architecture Azure', 'Services cloud', 'Réseaux Azure'],
        'description': 'Parcours de cinq modules sur l’architecture et les services principaux d’Azure.',
        'credential_info': 'Progression et réussite du parcours dans Microsoft Learn. Ce parcours ne vaut pas une certification Microsoft.',
    },
    {
        'title': 'Décrire la gestion et la gouvernance Azure',
        'platform': 'Microsoft Learn',
        'link': 'https://learn.microsoft.com/fr-fr/training/paths/describe-azure-management-governance/',
        'domain': 'Cloud',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['Gestion Azure', 'Gouvernance cloud', 'Surveillance'],
        'description': 'Parcours Microsoft Learn en quatre modules consacré à la gestion et à la gouvernance d’Azure.',
        'credential_info': 'Progression et réussite du parcours dans Microsoft Learn. Ce parcours ne vaut pas une certification professionnelle.',
    },
    {
        'title': 'Appliquer des compétences Azure dans des projets guidés',
        'platform': 'Microsoft Learn',
        'link': 'https://learn.microsoft.com/fr-fr/training/paths/introduction-cloud-infrastructure-apply-azure-skills-guided-projects/',
        'domain': 'Cloud',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['Pratique Azure', 'Infrastructure cloud'],
        'description': 'Parcours guidé de huit modules pour appliquer des compétences Azure à des projets.',
        'credential_info': 'Réussite suivie dans Microsoft Learn, pas une certification. Certains déploiements Azure peuvent entraîner des frais ; vérifier les tarifs et supprimer les ressources après usage.',
    },
    {
        'title': 'Votre premier site web',
        'platform': 'MDN Web Docs',
        'link': 'https://developer.mozilla.org/fr/docs/Learn_web_development/Getting_started/Your_first_website',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['HTML', 'CSS', 'Publication web'],
        'description': 'Guide gratuit de MDN pour planifier, créer et publier une première page web.',
        'credential_info': 'Ressource d’apprentissage gratuite ; aucun badge ni certificat n’est annoncé.',
    },
    {
        'title': 'Structurer le contenu avec HTML',
        'platform': 'MDN Web Docs',
        'link': 'https://developer.mozilla.org/fr/docs/Learn_web_development/Core/Structuring_content',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['HTML', 'Structure sémantique', 'Accessibilité'],
        'description': 'Ressource gratuite de MDN consacrée à la structure du contenu des pages web.',
        'credential_info': 'Ressource d’apprentissage gratuite ; aucun badge ni certificat n’est annoncé.',
    },
    {
        'title': 'Bases de la mise en forme CSS',
        'platform': 'MDN Web Docs',
        'link': 'https://developer.mozilla.org/fr/docs/Learn_web_development/Core/Styling_basics',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['CSS', 'Sélecteurs', 'Styles web'],
        'description': 'Guide gratuit de MDN pour comprendre les règles CSS et mettre en forme une page web.',
        'credential_info': 'Ressource d’apprentissage gratuite ; aucun badge ni certificat n’est annoncé.',
    },
    {
        'title': 'Premiers pas en JavaScript',
        'platform': 'MDN Web Docs',
        'link': 'https://developer.mozilla.org/fr/docs/Learn_web_development/Core/Scripting',
        'domain': 'Développement web',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français',
        'skills': ['JavaScript', 'Programmation web'],
        'description': 'Ressource gratuite de MDN pour découvrir les bases du scripting JavaScript dans le navigateur.',
        'credential_info': 'Ressource d’apprentissage gratuite ; aucun badge ni certificat n’est annoncé.',
    },
]


def seed_verified_courses(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias
    for course in COURSES:
        Formation.objects.using(database).update_or_create(
            title=course['title'],
            platform=course['platform'],
            defaults={
                **course,
                'link': course['link'],
                'is_free': True,
                'hosted_by_jupython': False,
                'last_verified_at': timezone.now(),
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0006_seed_jupython_learning_paths'),
    ]

    operations = [
        migrations.RunPython(seed_verified_courses, migrations.RunPython.noop),
    ]
