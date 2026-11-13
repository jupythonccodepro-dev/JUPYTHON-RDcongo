from django.db import migrations


COURSES = [
    {
        'title': 'Optimisez votre apprentissage avec l’Intelligence Artificielle',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/8248141-optimisez-votre-apprentissage-avec-l-intelligence-artificielle',
        'is_free': True,
        'description': 'Apprends à utiliser l’IA comme aide à l’apprentissage tout en gardant un regard critique sur les contenus générés.',
        'domain': 'Intelligence artificielle',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['IA générative', 'Rédaction de prompts', 'Esprit critique', 'Organisation des apprentissages'],
        'credential_info': 'Cours en libre accès. La page consultée ne confirme pas de certification professionnelle incluse.',
        'cover_image_url': 'https://course.oc-static.com/courses/8248141/8248141_teaser_picture_1739555010.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Initiez-vous au Machine Learning',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/8063076-initiez-vous-au-machine-learning',
        'is_free': True,
        'description': 'Découvre les principes du machine learning, prépare des données et entraîne des modèles prédictifs avec des exercices pratiques.',
        'domain': 'Intelligence artificielle',
        'level': 'Intermédiaire',
        'duration': '10 heures',
        'language': 'Français',
        'skills': ['Machine learning', 'Python', 'Régression', 'Classification', 'K-means'],
        'credential_info': 'Cours en libre accès. Des notions de Python, de statistiques et d’algèbre sont utiles pour suivre les exercices. Aucune certification professionnelle incluse n’est annoncée.',
        'cover_image_url': 'https://course.oc-static.com/courses/8063076/8063076_teaser_picture_1699278091.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Initiez-vous au Deep Learning',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/5801891-initiez-vous-au-deep-learning',
        'is_free': True,
        'description': 'Comprends les réseaux de neurones et les architectures utilisées pour traiter des images, du son et du texte.',
        'domain': 'Intelligence artificielle',
        'level': 'Intermédiaire',
        'duration': '8 heures',
        'language': 'Français',
        'skills': ['Deep learning', 'Réseaux de neurones', 'CNN', 'RNN', 'LSTM'],
        'credential_info': 'Cours en libre accès. Des bases en machine learning sont recommandées ; aucune certification professionnelle incluse n’est annoncée.',
        'cover_image_url': 'https://course.oc-static.com/courses/5801891/5801891_teaser_picture_1680857547.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Initiez-vous au ML Engineering',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/8681551-initiez-vous-au-ml-engineering',
        'is_free': True,
        'description': 'Passe du notebook à un modèle déployable en découvrant FastAPI, Docker, GitHub Actions et le suivi des expériences MLflow.',
        'domain': 'Intelligence artificielle',
        'level': 'Avancé',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['ML Engineering', 'FastAPI', 'Docker', 'GitHub Actions', 'MLflow'],
        'credential_info': 'Cours en libre accès. Des bases en préparation de données et en machine learning sont nécessaires ; aucune certification professionnelle incluse n’est annoncée.',
        'cover_image_url': 'https://course.oc-static.com/courses/8681551/8681551_teaser_picture_1764694642.jpg',
        'provider_logo_url': '',
    },
    {
        'title': 'Mettez en place un RAG pour un LLM',
        'platform': 'OpenClassrooms',
        'link': 'https://openclassrooms.com/fr/courses/8532116-mettez-en-place-un-rag-pour-un-llm',
        'is_free': True,
        'description': 'Apprends à construire un assistant fondé sur tes documents avec une base vectorielle, un modèle de langage et une interface de discussion.',
        'domain': 'Intelligence artificielle générative',
        'level': 'Avancé',
        'duration': '10 heures',
        'language': 'Français',
        'skills': ['IA générative', 'LLM', 'RAG', 'Bases vectorielles', 'Prompt système'],
        'credential_info': 'Cours en libre accès. Des bases en machine learning, deep learning et traitement de texte sont requises ; aucune certification professionnelle incluse n’est annoncée.',
        'cover_image_url': 'https://course.oc-static.com/courses/8532116/8532116_teaser_picture_1746002931.jpg',
        'provider_logo_url': '',
    },
]


def seed_external_ai_courses(apps, schema_editor):
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
        ('academy', '0020_more_external_courses'),
    ]

    operations = [
        migrations.RunPython(seed_external_ai_courses, migrations.RunPython.noop),
    ]
