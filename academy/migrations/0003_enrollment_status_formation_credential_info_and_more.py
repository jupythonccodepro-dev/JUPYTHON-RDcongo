# Généré par Django 6.0 le 2026-09-29 à 17:19

from django.db import migrations, models


COURSE_CATALOG = [
    {
        'title': 'Python Essentials 1',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/python-essentials-1?courseLang=fr-FR',
        'is_free': True,
        'description': 'Découvre les bases de Python à travers un parcours en autoformation proposé par Cisco Networking Academy.',
        'domain': 'Programmation',
        'level': 'Débutant',
        'duration': '30 heures',
        'language': 'Français',
        'skills': ['Bases de Python'],
        'credential_info': 'Badge de cours affiché par Cisco. Le cours prépare au PCEP, mais l’examen de certification PCEP n’est pas inclus.',
    },
    {
        'title': 'Introduction à la cybersécurité',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/introduction-to-cybersecurity?courseLang=fr-FR',
        'is_free': True,
        'description': 'Comprends les menaces numériques, les principes de sécurité et les premières pistes de carrière en cybersécurité.',
        'domain': 'Cybersécurité',
        'level': 'Débutant',
        'duration': '6 heures',
        'language': 'Français',
        'skills': ['Menaces informatiques', 'Protection des données', 'Principes de cybersécurité'],
        'credential_info': 'Aucun badge final ni certification professionnelle n’a pu être confirmé sur la page publique consultée.',
    },
    {
        'title': 'Notions de base sur la mise en réseau',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/networking-basics?courseLang=fr-FR',
        'is_free': True,
        'description': 'Apprends les notions fondamentales des réseaux informatiques avec un cours Cisco en autoformation.',
        'domain': 'Réseaux',
        'level': 'Débutant',
        'duration': '',
        'language': 'Français à confirmer sur la plateforme',
        'skills': ['Bases des réseaux informatiques'],
        'credential_info': 'La page consultée ne confirme pas de badge ni de certification professionnelle pour ce cours.',
    },
    {
        'title': 'Data Analytics Essentials',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/data-analytics-essentials?courseLang=fr-FR',
        'is_free': True,
        'description': 'Découvre l’analyse de données et travaille avec Excel, SQL et Tableau dans un parcours de niveau débutant.',
        'domain': 'Données',
        'level': 'Débutant',
        'duration': '30 heures',
        'language': 'Français partiel à confirmer sur la plateforme',
        'skills': ['Analyse de données', 'Excel', 'SQL', 'Tableau'],
        'credential_info': 'Cisco affiche un badge de cours et des badges de module. Ce parcours ne constitue pas une certification professionnelle.',
    },
    {
        'title': 'Python Essentials 2',
        'platform': 'Cisco Networking Academy',
        'link': 'https://www.netacad.com/courses/python-essentials-2?courseLang=en-US',
        'is_free': True,
        'description': 'Poursuis l’apprentissage de Python après les notions de base, avec un parcours en anglais.',
        'domain': 'Programmation',
        'level': 'Intermédiaire',
        'duration': '',
        'language': 'Anglais',
        'skills': ['Python niveau suivant'],
        'credential_info': 'Prépare à une certification Python externe. L’examen n’est pas inclus et le badge final n’a pas été confirmé sur la page consultée.',
    },
    {
        'title': 'Explore Emerging Tech',
        'platform': 'IBM SkillsBuild',
        'link': 'https://skills.yourlearning.ibm.com/activity/PLAN-B5FC126AEBFB',
        'is_free': True,
        'description': 'Explore des notions fondamentales sur les technologies émergentes, notamment les données, l’IA, le cloud et la cybersécurité.',
        'domain': 'Technologies numériques',
        'level': 'Débutant',
        'duration': '3 à 10 heures',
        'language': 'Langue à confirmer après connexion',
        'skills': ['Intelligence artificielle', 'Données', 'Cloud', 'Cybersécurité'],
        'credential_info': 'IBM annonce une attestation numérique (digital credential) pour ce parcours. Compte IBM SkillsBuild requis.',
    },
    {
        'title': 'Python for Beginners',
        'platform': 'Microsoft Learn',
        'link': 'https://learn.microsoft.com/en-us/shows/intro-to-python-development/',
        'is_free': True,
        'description': 'Série vidéo gratuite en anglais pour découvrir le développement avec Python, à suivre à son rythme.',
        'domain': 'Programmation',
        'level': 'Débutant',
        'duration': '',
        'language': 'Anglais',
        'skills': ['Syntaxe Python', 'Développement Python'],
        'credential_info': 'La page ne promet ni certificat ni badge de cours. Le compte Microsoft Learn est facultatif pour suivre la progression.',
    },
]


def seed_course_catalog(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    database = schema_editor.connection.alias

    for course in COURSE_CATALOG:
        Formation.objects.using(database).update_or_create(
            title=course['title'],
            platform=course['platform'],
            defaults=course,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0002_alter_academy_options_alter_certificate_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='status',
            field=models.CharField(choices=[('enrolled', 'Inscrit'), ('in_progress', 'En cours'), ('completed', 'Terminé')], default='enrolled', max_length=20),
        ),
        migrations.AddField(
            model_name='formation',
            name='credential_info',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='formation',
            name='domain',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='formation',
            name='duration',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='formation',
            name='language',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='formation',
            name='level',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='formation',
            name='skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(seed_course_catalog, migrations.RunPython.noop),
    ]
