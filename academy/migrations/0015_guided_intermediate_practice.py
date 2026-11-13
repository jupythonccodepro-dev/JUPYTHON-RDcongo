from django.db import migrations


GUIDED_PRACTICE = {
    'Modéliser les ressources et les contrats HTTP': (
        'À partir d’une application de tâches, définis GET /api/tasks/, POST /api/tasks/ et PATCH /api/tasks/{id}/. '
        'Pour chaque route, précise les champs d’entrée, un exemple JSON de réponse et les statuts d’erreur utiles.',
        'Un tableau méthode/URL/entrée/réponse suffit ; vérifie notamment 201 à la création, 400 si le titre est vide, '
        '401 sans connexion et qu’aucune réponse ne révèle les tâches d’un autre compte.',
    ),
    'Construire les modèles et les migrations Django': (
        'Écris le modèle Task avec propriétaire, titre, état et dates. Prévois les états « à faire », « en cours » et '
        '« terminée », puis ajoute un champ priorité dans une migration séparée.',
        'Rends le modèle et le plan de migration ; vérifie les valeurs par défaut pour les lignes existantes, '
        'les contraintes en base et la possibilité d’appliquer la migration sur une base vide.',
    ),
    'Sérialise les données et valide les entrées': (
        'Prépare un serializer de création de tâche. Teste un titre valide, un titre vide, un état inconnu et une '
        'requête qui tente d’envoyer owner_id.',
        'Fournis les entrées et réponses attendues ; le propriétaire doit être assigné côté serveur et les erreurs '
        'doivent nommer le champ invalide sans exposer de trace technique.',
    ),
    'Filtrer par utilisateur et appliquer les permissions': (
        'Crée deux comptes fictifs, Alice et Bob, et une tâche appartenant à Alice. Vérifie les actions de liste, '
        'lecture par identifiant, modification et suppression depuis la session de Bob.',
        'Rends une matrice action/résultat attendu ; aucune route ne doit révéler ni modifier la tâche d’Alice pour Bob, '
        'même si Bob connaît son identifiant.',
    ),
    'Tester les succès, les erreurs et l’isolation': (
        'Construis une suite de tests d’API couvrant création valide, titre invalide, liste personnelle, suppression, '
        'requête anonyme et accès croisé entre Alice et Bob.',
        'Fournis les noms de tests et les statuts attendus ; chaque test doit créer ses propres données et vérifier '
        'aussi qu’une erreur ne modifie pas la base.',
    ),
    'Gérer les secrets, les limites et la documentation': (
        'Passe en revue une configuration fictive avant lancement : secret dans le dépôt, API sans HTTPS, route sans '
        'limitation et documentation absente. Propose un correctif pour chaque constat.',
        'Rends une checklist avec responsable et preuve de contrôle ; aucun secret ne doit être versionné et les limites '
        'doivent être testées sans bloquer abusivement les usages normaux.',
    ),
    'Lire des journaux d’authentification et de réseau': (
        'Analyse cette séquence fictive en UTC : 09:02 échec de connexion pour sam depuis 203.0.113.24 ; 09:04 succès '
        'pour sam depuis la même adresse ; 09:06 résolution DNS inhabituelle depuis le poste LT-07. Établis les liens '
        'possibles sans conclure au-delà des faits.',
        'Rends une chronologie, les comptes et actifs concernés, les faits, les hypothèses et les éléments manquants ; '
        'les heures doivent rester dans le même fuseau et les journaux originaux être préservés.',
    ),
    'Trier une alerte de sécurité': (
        'Un compte standard se connecte depuis un nouvel emplacement après plusieurs échecs. Prépare le triage en '
        'précisant les vérifications nécessaires avant de suspendre le compte.',
        'Rends une fiche avec source du signal, actif, faits, impact potentiel, urgence, prochaine vérification et '
        'critère d’escalade ; sépare clairement les faits des hypothèses.',
    ),
    'Préserver les preuves et limiter l’impact': (
        'Dans un exercice sur un compte fictif supposé compromis, prépare les premières actions selon une procédure '
        'd’équipe : qui autorise la révocation de session, qui préserve les journaux et qui informe le responsable ?',
        'Rends un plan horodatable avec action, responsable, autorisation et preuve à conserver ; n’effectue aucune '
        'action sur un compte ou système réel.',
    ),
    'Enquêter sur un message de phishing': (
        'Étudie un courriel fictif dont From est formation@jupython-support.example, Reply-To est '
        'aide@connexion-verif.example et le lien affiché mène à un autre domaine. Liste les vérifications à mener '
        'sans ouvrir le lien ni la pièce jointe.',
        'Rends les indices observés, les destinataires à vérifier, les mesures de précaution et un message d’alerte '
        'neutre ; indique ce qui reste incertain et utilise uniquement des données fictives.',
    ),
    'Prioriser les correctifs et les accès': (
        'Compare trois actifs fictifs : un serveur public avec correctif critique, un poste interne avec correctif '
        'important et un compte administrateur partagé. Classe les risques selon exposition, impact et mesures existantes.',
        'Rends un classement justifié et un plan avec responsable, échéance, contrôle après correction et réduction '
        'des privilèges ; ne te base pas uniquement sur le score technique.',
    ),
    'Rédiger un rapport de fin d’incident': (
        'À partir du scénario de phishing étudié, rédige le plan d’un rapport destiné à la direction et transforme '
        'deux constats en actions vérifiables.',
        'Le rapport distingue faits, hypothèses et inconnues ; chaque action possède un responsable, une échéance et '
        'une preuve de validation, sans exposer de donnée personnelle inutile.',
    ),
    'Définir une question avant d’analyser': (
        'Une équipe dit « les ventes baissent ». Reformule ce besoin en trois questions mesurables : évolution par mois, '
        'comparaison par région et effet des annulations, en indiquant pour chacune la période et l’unité d’analyse.',
        'Rends une fiche question/indicateur/source/unité/période ; définis le chiffre d’affaires retenu et ne présente '
        'pas une corrélation comme une cause.',
    ),
    'Contrôler un CSV avec Pandas': (
        'Audite un CSV fictif de ventes contenant une date au format différent, un montant manquant, une commande '
        'dupliquée et une remise de 140 %. Décris les contrôles Pandas à exécuter avant tout calcul.',
        'Rends un rapport anomalies/décision/justification ; conserve la source brute, distingue les données manquantes '
        'des erreurs et rends les corrections rejouables.',
    ),
    'Joindre et agréger des tables SQL': (
        'Utilise des tables fictives customers(id, region) et orders(id, customer_id, amount). Écris la requête '
        'de total des commandes par région et explique comment un client avec plusieurs commandes affecte la jointure.',
        'Rends la requête avec une agrégation par région et un contrôle du nombre de lignes et du total avant/après '
        'jointure pour détecter un doublonnage.',
    ),
    'Calculer des indicateurs fiables avec Pandas': (
        'Sur un DataFrame fictif contenant status, amount et discount, définis le calcul des ventes nettes en excluant '
        'les commandes annulées et en appliquant les remises.',
        'Rends la formule, les étapes de transformation et trois contrôles : nombre de lignes exclues, total de contrôle '
        'et vérification manuelle d’une commande ; documente les valeurs manquantes.',
    ),
    'Choisir une visualisation sans induire en erreur': (
        'Prépare une vue des ventes mensuelles de quatre régions. Choisis un graphique pour la tendance et un autre '
        'pour comparer les régions, puis rédige leurs titres et unités.',
        'Rends deux graphiques lisibles avec période, unité, source et légende ; les axes ne doivent pas exagérer les '
        'écarts et la couleur ne doit pas être l’unique moyen de distinguer les séries.',
    ),
    'Présenter les résultats avec leurs limites': (
        'Écris une synthèse de cinq phrases pour un responsable : résultat, preuve, recommandation, limite et prochain '
        'contrôle à réaliser.',
        'Chaque affirmation chiffrée renvoie à une mesure vérifiée ; distingue observation et interprétation, formule '
        'une action mesurable et signale les données manquantes.',
    ),
    'Organiser les branches et les changements Git': (
        'Prépare la livraison d’une nouvelle route API : crée une branche dédiée, sépare les changements en commits, '
        'prévois la revue et indique quand lancer les tests avant la fusion.',
        'Rends une séquence de commandes ou d’étapes vérifiable ; le diff est relu, aucun secret ni fichier généré '
        'n’est inclus et les tests passent avant la fusion.',
    ),
    'Construire une pipeline de tests': (
        'Conçois une pipeline Django qui installe les dépendances verrouillées, lance les contrôles et tests, puis '
        'construit un artefact uniquement si tout réussit.',
        'Rends les étapes dans l’ordre, les conditions d’échec, les secrets nécessaires et l’artefact ; un échec de '
        'test doit bloquer la livraison et aucun secret ne doit apparaître dans les logs.',
    ),
    'Construire une image Docker maîtrisée': (
        'Dans un Dockerfile fictif, repère COPY .env, l’exécution en root, l’envoi de .git et d’un environnement virtuel, '
        'puis des dépendances installées sans version fixée.',
        'Rends un diff ou une liste de corrections ; le build exclut les secrets et caches, fixe les dépendances et '
        'exécute l’application avec des privilèges minimaux.',
    ),
    'Configurer l’application et ses services': (
        'Décris une application web avec PostgreSQL en développement puis en production : variables, réseau, volume, '
        'contrôle de disponibilité, stratégie de migration et sauvegarde.',
        'Rends un schéma de services et une checklist de démarrage ; les identifiants ne sont pas dans l’image, le '
        'stockage persiste et la disponibilité de la base est vérifiée avant les opérations dépendantes.',
    ),
    'Déployer avec des contrôles de santé': (
        'Prépare une livraison avec vérification de l’artefact, contrôle de santé après déploiement, seuils d’arrêt '
        'sur erreurs et procédure de retour à la version précédente.',
        'Rends les contrôles avant/après, les seuils observables et les étapes de rollback ; précise les migrations '
        'compatibles et le responsable de la décision d’arrêt.',
    ),
    'Lire des journaux et préparer les sauvegardes': (
        'Élabore une checklist d’exploitation pour ton projet : journaux structurés, métriques, alerte, fréquence de '
        'sauvegarde et test de restauration dans un environnement isolé.',
        'Rends un calendrier avec responsable, rétention, objectif de restauration et preuve d’un test réussi ; aucun '
        'mot de passe, jeton ou contenu privé ne figure dans les journaux.',
    ),
}

DELIVERABLES = {
    'Modéliser les ressources et les contrats HTTP': 'un contrat HTTP pour les trois routes avec exemples de réponses JSON',
    'Construire les modèles et les migrations Django': 'le modèle Task et un plan de migration pour le champ priorité',
    'Sérialise les données et valide les entrées': 'un tableau des cas d’entrée et des réponses de validation attendues',
    'Filtrer par utilisateur et appliquer les permissions': 'une matrice d’accès Alice/Bob et les tests d’isolation associés',
    'Tester les succès, les erreurs et l’isolation': 'un plan de tests avec cas, assertions et statuts attendus',
    'Gérer les secrets, les limites et la documentation': 'une checklist de lancement avec responsable et preuve de contrôle',
    'Lire des journaux d’authentification et de réseau': 'une chronologie des événements et une liste des inconnues à vérifier',
    'Trier une alerte de sécurité': 'une fiche de triage documentant le signal et la décision d’escalade',
    'Préserver les preuves et limiter l’impact': 'un plan de confinement avec les rôles et preuves à préserver',
    'Enquêter sur un message de phishing': 'un rapport d’analyse et un message d’alerte destiné aux utilisateurs',
    'Prioriser les correctifs et les accès': 'un classement des risques et un plan d’actions correctives',
    'Rédiger un rapport de fin d’incident': 'un rapport d’incident synthétique et deux actions mesurables',
    'Définir une question avant d’analyser': 'une fiche de cadrage avec questions, indicateurs, sources et périodes',
    'Contrôler un CSV avec Pandas': 'un rapport d’audit des données avec les décisions de nettoyage',
    'Joindre et agréger des tables SQL': 'la requête SQL et ses contrôles de cardinalité et de total',
    'Calculer des indicateurs fiables avec Pandas': 'un calcul reproductible des ventes nettes et ses résultats de contrôle',
    'Choisir une visualisation sans induire en erreur': 'deux visualisations légendées et justifiées',
    'Présenter les résultats avec leurs limites': 'une synthèse décisionnelle de cinq phrases',
    'Organiser les branches et les changements Git': 'une séquence Git et une checklist de revue avant fusion',
    'Construire une pipeline de tests': 'un diagramme de pipeline avec étapes, conditions et artefact',
    'Construire une image Docker maîtrisée': 'une revue du Dockerfile avec les corrections proposées',
    'Configurer l’application et ses services': 'un schéma de services et une checklist de configuration par environnement',
    'Déployer avec des contrôles de santé': 'un plan de déploiement, critères d’arrêt et étapes de retour arrière',
    'Lire des journaux et préparer les sauvegardes': 'une checklist d’exploitation et un protocole de test de restauration',
}

MARKER = '\n\nAtelier pratique guidé\n'


def add_guided_practice(apps, schema_editor):
    CourseLesson = apps.get_model('academy', 'CourseLesson')
    database = schema_editor.connection.alias
    lessons = CourseLesson.objects.using(database).filter(
        module__formation__hosted_by_jupython=True,
        module__formation__level='Intermédiaire',
        module__formation__platform='Jupython',
    )

    for lesson in lessons:
        guide = GUIDED_PRACTICE.get(lesson.title)
        if not guide or MARKER in lesson.exercise:
            continue
        scenario, criteria = guide
        deliverable = DELIVERABLES[lesson.title]
        lesson.exercise = (
            f'{lesson.exercise}{MARKER}{scenario}\n\n'
            f'Livrable attendu : {deliverable}.\n'
            f'Critères de réussite : {criteria}'
        )
        lesson.save(update_fields=['exercise'])


def remove_guided_practice(apps, schema_editor):
    CourseLesson = apps.get_model('academy', 'CourseLesson')
    database = schema_editor.connection.alias
    lessons = CourseLesson.objects.using(database).filter(exercise__contains=MARKER)
    for lesson in lessons:
        lesson.exercise = lesson.exercise.split(MARKER, 1)[0]
        lesson.save(update_fields=['exercise'])


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0014_seed_module_quizzes'),
    ]

    operations = [
        migrations.RunPython(add_guided_practice, remove_guided_practice),
    ]
