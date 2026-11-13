from django.db import migrations


QUIZZES = {
    'Découvrir Python': [
        ('Que contient une variable après l’instruction total = 3 ?', ['Le nombre 3', 'Le texte total', 'Le nom du fichier'], 0),
        ('Quel type convient à une quantité entière ?', ['str', 'int', 'bool'], 1),
        ('Pourquoi donner un nom explicite à une variable ?', ['Pour éviter de tester le code', 'Pour rendre son rôle compréhensible', 'Pour la rendre globale'], 1),
    ],
    'Faire des choix et répéter des actions': [
        ('Quelle instruction exécute un bloc seulement si une condition est vraie ?', ['if', 'for', 'def'], 0),
        ('Quand une boucle for est-elle généralement adaptée ?', ['Pour parcourir une séquence', 'Pour déclarer une classe', 'Pour convertir une chaîne'], 0),
        ('Quel risque faut-il contrôler dans une boucle while ?', ['Une boucle qui ne se termine jamais', 'Une variable qui devient une fonction', 'Une table SQL vide'], 0),
    ],
    'Réutiliser et vérifier son code': [
        ('Quel est l’intérêt principal d’une fonction ?', ['Réutiliser un bloc de code nommé', 'Masquer toutes les erreurs', 'Remplacer les variables'], 0),
        ('Que fournit return dans une fonction ?', ['Une valeur au code appelant', 'Un nouveau module Python', 'Une entrée clavier automatique'], 0),
        ('Quelle est une première étape utile pour déboguer ?', ['Lire le message d’erreur et localiser la ligne', 'Supprimer les tests', 'Ignorer la trace'], 0),
    ],
    'Structurer une page avec HTML': [
        ('Quel élément décrit le contenu principal d’une page ?', ['<main>', '<span>', '<i>'], 0),
        ('À quoi sert un attribut alt pertinent sur une image informative ?', ['À décrire l’image aux technologies d’assistance', 'À agrandir l’image', 'À charger le CSS'], 0),
        ('Quel élément convient pour un titre de premier niveau ?', ['<h1>', '<strong>', '<title> dans le corps'], 0),
    ],
    'Présenter avec CSS': [
        ('Quel sélecteur cible un élément portant class="carte" ?', ['.carte', '#carte', 'carte()'], 0),
        ('Quelles zones composent le modèle de boîte CSS ?', ['Contenu, padding, bordure et marge', 'Titre, script et lien', 'Clé, index et table'], 0),
        ('Quelle règle aide une mise en page à s’adapter aux petits écrans ?', ['Une media query', 'Un commentaire HTML', 'Un attribut alt'], 0),
    ],
    'Découvrir les bases de données': [
        ('À quoi sert une clé primaire ?', ['À identifier chaque ligne de manière unique', 'À trier automatiquement toutes les colonnes', 'À stocker les mots de passe en clair'], 0),
        ('Dans une base relationnelle, une table représente principalement…', ['Un ensemble d’enregistrements d’un même type', 'Une page de styles', 'Une fonction Python'], 0),
        ('Quelle contrainte empêche deux lignes d’avoir la même valeur de clé primaire ?', ['UNIQUE et PRIMARY KEY', 'ORDER BY', 'LIKE'], 0),
    ],
    'Filtrer et ordonner les résultats': [
        ('Quelle clause sélectionne les lignes qui respectent un critère ?', ['WHERE', 'VALUES', 'CREATE'], 0),
        ('Quelle clause trie les résultats d’une requête ?', ['ORDER BY', 'GROUP BY uniquement', 'INSERT INTO'], 0),
        ('Comment éviter une injection SQL avec une valeur fournie par l’utilisateur ?', ['Utiliser des paramètres de requête', 'Concaténer la valeur dans SQL', 'Désactiver les validations'], 0),
    ],
    'Concevoir une API et son modèle de données': [
        ('Quelle méthode HTTP convient normalement pour lire une ressource sans la modifier ?', ['GET', 'DELETE', 'PATCH'], 0),
        ('Quel statut HTTP indique habituellement qu’une ressource a été créée ?', ['201', '404', '500'], 0),
        ('Pourquoi ajouter une contrainte d’unicité au modèle et à la base ?', ['Pour faire respecter une règle même en cas de requêtes concurrentes', 'Pour remplacer les migrations', 'Pour rendre tous les champs facultatifs'], 0),
    ],
    'Implémenter, valider et sécuriser les endpoints': [
        ('Quel est le rôle principal d’un serializer DRF ?', ['Valider et transformer les données échangées', 'Exécuter les migrations SQL', 'Démarrer le serveur web'], 0),
        ('D’où doit venir le propriétaire d’un objet créé par un utilisateur connecté ?', ['De request.user côté serveur', 'Du champ owner envoyé librement par le client', 'Du premier utilisateur en base'], 0),
        ('Que doit retourner une API si un utilisateur authentifié n’a pas le droit d’accéder à un objet ?', ['Un refus d’accès sans exposer les données privées', 'Le contenu puis un avertissement', 'Une trace complète du serveur'], 0),
    ],
    'Tester et préparer la livraison': [
        ('Que doit vérifier un test d’isolation entre deux comptes ?', ['Un compte ne peut pas lire ou modifier les objets de l’autre', 'Les deux comptes ont le même mot de passe', 'La base accepte chaque entrée'], 0),
        ('Où conserver une clé secrète de production ?', ['Dans une variable d’environnement ou un gestionnaire de secrets', 'Dans le dépôt Git public', 'Dans le code JavaScript livré au navigateur'], 0),
        ('À quoi sert une documentation OpenAPI ?', ['À décrire les routes, entrées et réponses de l’API', 'À chiffrer automatiquement la base', 'À remplacer les tests'], 0),
    ],
    'Comprendre les traces et les signaux': [
        ('Quel élément aide à reconstituer une chronologie d’incident ?', ['Des journaux horodatés et leur fuseau connu', 'Une capture sans date', 'Une supposition non vérifiée'], 0),
        ('Quel est le bon premier réflexe face à une alerte de sécurité ?', ['Vérifier les éléments observables et le contexte', 'Supprimer immédiatement les journaux', 'Accuser un utilisateur sans vérification'], 0),
        ('Pourquoi corréler plusieurs sources de journaux ?', ['Pour confirmer ou infirmer un signal avec des indices indépendants', 'Pour effacer les événements répétés', 'Pour éviter de documenter l’incident'], 0),
    ],
    'Conduire une réponse à incident': [
        ('Pourquoi préserver les preuves avant une investigation ?', ['Pour conserver des éléments fiables et exploitables', 'Pour accélérer la suppression des comptes', 'Pour éviter toute journalisation'], 0),
        ('Que faire face à un message de phishing suspect ?', ['Analyser les en-têtes et liens sans ouvrir de contenu risqué', 'Répondre avec ses identifiants', 'Transférer le message à tous les contacts'], 0),
        ('Quel ordre correspond le mieux à une réponse structurée ?', ['Détecter, contenir, éradiquer, restaurer et tirer les leçons', 'Restaurer, supprimer les preuves, puis détecter', 'Publier les données, puis enquêter'], 0),
    ],
    'Réduire le risque et rendre compte': [
        ('Comment prioriser un correctif de sécurité ?', ['Selon le risque, l’exposition et l’impact', 'Selon l’ordre alphabétique des serveurs', 'En ignorant les actifs exposés'], 0),
        ('Quel principe réduit les risques liés aux comptes ?', ['Accorder le minimum de privilèges nécessaires', 'Partager un compte administrateur', 'Désactiver la MFA'], 0),
        ('Que doit contenir un rapport de fin d’incident ?', ['Chronologie, impact, actions et recommandations', 'Des hypothèses présentées comme des faits', 'Les secrets d’accès en clair'], 0),
    ],
    'Inspecter et préparer des données': [
        ('Pourquoi définir une question avant d’analyser un jeu de données ?', ['Pour choisir des mesures utiles à une décision précise', 'Pour garantir un résultat favorable', 'Pour éviter de vérifier les données'], 0),
        ('Quel contrôle est pertinent lors de l’import d’un CSV avec Pandas ?', ['Types, valeurs manquantes, doublons et plages plausibles', 'Uniquement la couleur des cellules', 'La suppression de toutes les lignes rares'], 0),
        ('Que faire si les unités ou définitions d’une colonne sont inconnues ?', ['Les clarifier avant d’interpréter les chiffres', 'Inventer une unité', 'Publier le graphique sans note'], 0),
    ],
    'Analyser et vérifier les résultats': [
        ('Quelle condition évite une jointure SQL accidentelle de toutes les lignes ?', ['Une clé de jointure appropriée et vérifiée', 'Un alias plus court', 'Un ORDER BY'], 0),
        ('Pourquoi contrôler le nombre de lignes après une jointure ?', ['Pour détecter doublons ou pertes inattendues', 'Pour vérifier le format des couleurs', 'Pour supprimer les clés étrangères'], 0),
        ('Comment traiter un indicateur dont les valeurs semblent aberrantes ?', ['Examiner la source et documenter la règle de traitement', 'Les supprimer sans trace', 'Les remplacer toutes par zéro'], 0),
    ],
    'Communiquer une recommandation': [
        ('Quelle visualisation convient à une évolution dans le temps ?', ['Une courbe avec axes et période clairement indiqués', 'Un nuage de mots sans légende', 'Un camembert 3D par défaut'], 0),
        ('Pourquoi signaler les limites d’une analyse ?', ['Pour éviter une conclusion plus forte que les données', 'Pour rendre les chiffres inutilisables', 'Pour cacher les hypothèses'], 0),
        ('Quelle recommandation aide le mieux une équipe métier ?', ['Une action claire reliée aux résultats et à leurs limites', 'Un chiffre sans contexte', 'Une liste de graphiques sans conclusion'], 0),
    ],
    'Structurer le code et automatiser les vérifications': [
        ('Pourquoi utiliser des branches Git pour une modification ?', ['Isoler le travail et faciliter la revue', 'Supprimer l’historique', 'Partager directement les secrets'], 0),
        ('Quel est l’intérêt d’une pipeline de tests en intégration continue ?', ['Détecter rapidement les régressions à chaque changement', 'Éviter d’écrire des tests', 'Remplacer la revue de code'], 0),
        ('Que faut-il faire si un test de la pipeline échoue ?', ['Examiner l’échec et corriger avant la livraison', 'Masquer le résultat', 'Déployer sans vérifier'], 0),
    ],
    'Conteneuriser sans cacher les risques': [
        ('Quel principe réduit la taille et la surface d’attaque d’une image ?', ['Utiliser une image de base minimale et maîtrisée', 'Inclure tous les outils de développement', 'Exécuter systématiquement en root'], 0),
        ('Où configurer les secrets nécessaires à un conteneur ?', ['Dans un mécanisme de secrets ou variables protégées', 'Dans l’image construite', 'Dans un fichier suivi par Git'], 0),
        ('Pourquoi fixer ou contrôler les versions des images de base ?', ['Pour rendre les builds reproductibles et maîtriser les mises à jour', 'Pour empêcher tout correctif', 'Pour désactiver les tests'], 0),
    ],
    'Livrer, surveiller et revenir en arrière': [
        ('À quoi sert un contrôle de santé après déploiement ?', ['À vérifier que le service répond correctement', 'À remplacer les sauvegardes', 'À supprimer les journaux'], 0),
        ('Quel signal aide à investiguer une erreur de production ?', ['Des journaux structurés avec contexte et horodatage', 'Un secret copié dans un ticket public', 'Une capture sans information'], 0),
        ('Pourquoi préparer une procédure de retour arrière ?', ['Pour restaurer rapidement une version stable si la livraison échoue', 'Pour éviter de tester la livraison', 'Pour supprimer les données sans vérification'], 0),
    ],
}


def seed_quizzes(apps, schema_editor):
    CourseModule = apps.get_model('academy', 'CourseModule')
    ModuleQuizQuestion = apps.get_model('academy', 'ModuleQuizQuestion')
    database = schema_editor.connection.alias

    for module in CourseModule.objects.using(database).filter(formation__hosted_by_jupython=True):
        questions = QUIZZES.get(module.title)
        if not questions:
            continue
        for order, (prompt, choices, correct_choice) in enumerate(questions, start=1):
            choice_options = list(choices)
            correct_position = (order + module.id) % len(choice_options)
            answer = choice_options.pop(correct_choice)
            choice_options.insert(correct_position, answer)
            ModuleQuizQuestion.objects.using(database).get_or_create(
                module_id=module.id,
                order=order,
                defaults={
                    'prompt': prompt,
                    'choices': choice_options,
                    'correct_choice': correct_position,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0013_modulequizquestion_modulequizprogress'),
    ]

    operations = [
        migrations.RunPython(seed_quizzes, migrations.RunPython.noop),
    ]
