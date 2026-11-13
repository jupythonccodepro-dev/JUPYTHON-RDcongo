from django.db import migrations
from django.utils import timezone


LEARNING_PATHS = [
    {
        'title': 'Python pratique : les fondamentaux',
        'domain': 'Programmation',
        'duration': '3 heures',
        'skills': ['Variables', 'Conditions', 'Boucles', 'Fonctions'],
        'credential_info': 'Le suivi du parcours développe des compétences mais ne vaut pas certification professionnelle. Les éventuels certificats Cisco sont gérés et délivrés par Cisco.',
        'modules': [
            {
                'title': 'Découvrir Python',
                'description': 'Prépare ton environnement et écris tes premières instructions.',
                'lessons': [
                    {
                        'title': 'À quoi sert Python ?',
                        'duration': 15,
                        'objectives': ['Identifier des usages de Python', 'Comprendre le rôle d’un interpréteur'],
                        'content': (
                            'Python est un langage utilisé pour automatiser des tâches, créer des applications web, '
                            'analyser des données et expérimenter en intelligence artificielle. Son code est conçu pour '
                            'rester lisible : les blocs sont notamment délimités par leur indentation.\n\n'
                            'Un programme est une suite d’instructions exécutées par l’interpréteur Python. Pour apprendre, '
                            'tu peux installer Python sur ton ordinateur ou utiliser un environnement de programmation en ligne.'
                        ),
                        'exercise': 'Note trois tâches de ton quotidien que tu pourrais automatiser avec un programme.',
                    },
                    {
                        'title': 'Afficher des informations et utiliser des variables',
                        'duration': 20,
                        'objectives': ['Afficher un message avec print()', 'Stocker une valeur dans une variable'],
                        'content': (
                            'La fonction print() affiche une information. Une variable associe un nom à une valeur, par '
                            'exemple nom = "Amina" ou age = 20. Le signe égal affecte la valeur à la variable ; il ne '
                            'signifie pas que l’on pose une équation.\n\n'
                            'Les textes sont entourés de guillemets. Les nombres peuvent être entiers ou décimaux. Choisis '
                            'des noms de variables qui décrivent les informations qu’ils contiennent.'
                        ),
                        'exercise': 'Écris un petit programme qui stocke ton prénom et ton objectif d’apprentissage dans deux variables puis les affiche.',
                    },
                ],
            },
            {
                'title': 'Faire des choix et répéter des actions',
                'description': 'Utilise les conditions et les boucles pour donner un comportement à ton programme.',
                'lessons': [
                    {
                        'title': 'Prendre une décision avec if',
                        'duration': 20,
                        'objectives': ['Comparer des valeurs', 'Écrire une condition if/else indentée'],
                        'content': (
                            'Une condition permet d’exécuter des instructions différentes selon une situation. En Python, '
                            'if teste une condition et else décrit le cas contraire. Les opérateurs courants sont ==, !=, '
                            '<, >, <= et >=. Le mot and combine deux conditions ; or accepte l’une ou l’autre.\n\n'
                            'Après les deux-points, indente les instructions qui appartiennent au bloc. Une indentation '
                            'cohérente est nécessaire pour que Python comprenne la structure.'
                        ),
                        'exercise': 'Crée une variable note et affiche « Réussi » si elle vaut au moins 50, sinon « À retravailler ».',
                    },
                    {
                        'title': 'Répéter avec for et while',
                        'duration': 25,
                        'objectives': ['Parcourir une suite avec for', 'Reconnaître le risque d’une boucle while infinie'],
                        'content': (
                            'Une boucle for répète un bloc pour chaque élément d’une séquence. range(5) produit cinq '
                            'valeurs, de 0 à 4. Une boucle while répète tant qu’une condition reste vraie ; il faut '
                            'donc faire évoluer cette condition pour éviter une boucle infinie.\n\n'
                            'Les boucles évitent de copier plusieurs fois les mêmes instructions et rendent les traitements '
                            'de listes plus simples.'
                        ),
                        'exercise': 'Affiche les nombres de 1 à 10 avec une boucle, puis affiche uniquement ceux qui sont pairs.',
                    },
                ],
            },
            {
                'title': 'Réutiliser et vérifier son code',
                'description': 'Organise des instructions dans des fonctions et vérifie les résultats.',
                'lessons': [
                    {
                        'title': 'Créer une fonction',
                        'duration': 25,
                        'objectives': ['Définir une fonction avec def', 'Retourner un résultat avec return'],
                        'content': (
                            'Une fonction regroupe des instructions sous un nom réutilisable. On la définit avec def, '
                            'on peut lui transmettre des paramètres et return renvoie un résultat à l’appelant.\n\n'
                            'Une fonction bien nommée réalise une tâche claire. Découper un programme en fonctions aide '
                            'à comprendre, tester et modifier le code.'
                        ),
                        'exercise': 'Écris une fonction aire_rectangle(longueur, largeur) qui renvoie le produit de ses paramètres.',
                    },
                    {
                        'title': 'Déboguer un petit programme',
                        'duration': 20,
                        'objectives': ['Lire un message d’erreur simple', 'Tester plusieurs valeurs'],
                        'content': (
                            'Un message d’erreur Python indique souvent le type de problème et la ligne concernée. '
                            'SyntaxError signale une écriture invalide ; NameError indique un nom introuvable ; '
                            'TypeError apparaît lorsqu’une opération ne convient pas aux types reçus.\n\n'
                            'Lis la dernière ligne du message, vérifie la ligne indiquée et reproduis le problème avec '
                            'un exemple minimal. Après une correction, relance le programme pour vérifier le résultat.'
                        ),
                        'exercise': 'Provoque puis corrige une NameError en utilisant une variable avant de l’avoir définie.',
                    },
                ],
            },
        ],
    },
    {
        'title': 'Créer ses premières pages web',
        'domain': 'Développement web',
        'duration': '2 heures',
        'skills': ['HTML', 'Structure web', 'CSS', 'Mise en page'],
        'credential_info': 'Le suivi du parcours développe des compétences mais ne vaut pas certification professionnelle. Aucun certificat externe n’est inclus.',
        'modules': [
            {
                'title': 'Structurer une page avec HTML',
                'description': 'Découvre les éléments qui donnent du sens au contenu d’une page.',
                'lessons': [
                    {
                        'title': 'Le squelette d’un document HTML',
                        'duration': 20,
                        'objectives': ['Reconnaître les balises HTML', 'Distinguer head et body'],
                        'content': (
                            'HTML décrit la structure et le sens du contenu d’une page. Un document standard contient '
                            'la déclaration doctype, l’élément html, un head pour les métadonnées et un body pour le '
                            'contenu visible.\n\n'
                            'Les balises s’ouvrent et se ferment autour du contenu. Un titre de page se place dans title ; '
                            'les titres visibles utilisent h1 à h6 et les paragraphes utilisent p.'
                        ),
                        'exercise': 'Rédige le squelette HTML d’une page de présentation avec un titre, un paragraphe et une liste de trois objectifs.',
                    },
                    {
                        'title': 'Rendre le contenu accessible',
                        'duration': 20,
                        'objectives': ['Choisir une hiérarchie de titres logique', 'Écrire un texte alternatif pour une image'],
                        'content': (
                            'Utilise les éléments HTML selon leur rôle : nav pour la navigation, main pour le contenu '
                            'principal, article pour un contenu autonome et footer pour le pied de page. Une page doit '
                            'généralement avoir un seul h1 puis des sous-titres dans un ordre logique.\n\n'
                            'Une image informative doit avoir un attribut alt qui en décrit l’information utile. Un lien '
                            'doit annoncer sa destination ou son action, plutôt que d’afficher uniquement « cliquer ici ».'
                        ),
                        'exercise': 'Ajoute à ta page une navigation, une section principale et une image avec un texte alternatif descriptif.',
                    },
                ],
            },
            {
                'title': 'Présenter avec CSS',
                'description': 'Applique une apparence cohérente et adapte la page aux petits écrans.',
                'lessons': [
                    {
                        'title': 'Appliquer des styles CSS',
                        'duration': 20,
                        'objectives': ['Écrire une règle CSS', 'Sélectionner un élément HTML par balise ou classe'],
                        'content': (
                            'CSS contrôle l’apparence des éléments HTML. Une règle CSS associe un sélecteur à des '
                            'déclarations entre accolades. Chaque déclaration associe une propriété à une valeur, '
                            'par exemple color: orange;.\n\n'
                            'Une classe, définie dans HTML avec class, permet de réutiliser un style. Une feuille externe '
                            'se relie au document avec link dans le head ; cette séparation facilite la maintenance.'
                        ),
                        'exercise': 'Crée une classe bouton et applique-lui une couleur de fond, une couleur de texte et un espacement intérieur.',
                    },
                    {
                        'title': 'Créer une mise en page adaptée au mobile',
                        'duration': 25,
                        'objectives': ['Utiliser Flexbox ou Grid', 'Ajouter une règle responsive avec media queries'],
                        'content': (
                            'Flexbox et CSS Grid organisent les éléments sans recourir à des positions fixes. Avec '
                            'flex-wrap, une rangée peut passer à la ligne ; avec Grid, repeat et minmax permettent de '
                            'créer des colonnes qui s’adaptent à l’espace disponible.\n\n'
                            'Une media query applique des styles selon la largeur de l’écran. Prévois des boutons '
                            'faciles à toucher, un texte lisible et aucune barre de défilement horizontale.'
                        ),
                        'exercise': 'Présente deux cartes côte à côte sur grand écran puis l’une sous l’autre sur un petit écran.',
                    },
                ],
            },
        ],
    },
    {
        'title': 'SQL : interroger des données',
        'domain': 'Données',
        'duration': '2 heures',
        'skills': ['Bases de données relationnelles', 'SELECT', 'WHERE', 'ORDER BY'],
        'credential_info': 'Le suivi du parcours développe des compétences mais ne vaut pas certification professionnelle. Aucun certificat externe n’est inclus.',
        'modules': [
            {
                'title': 'Découvrir les bases de données',
                'description': 'Comprends les tables, les colonnes et les enregistrements.',
                'lessons': [
                    {
                        'title': 'Organiser des informations en tables',
                        'duration': 20,
                        'objectives': ['Décrire une table relationnelle', 'Comprendre le rôle d’une clé primaire'],
                        'content': (
                            'Une base de données relationnelle organise les informations en tables. Une table contient '
                            'des colonnes décrivant les propriétés et des lignes représentant les enregistrements. '
                            'Chaque colonne possède un type, comme un nombre, du texte ou une date.\n\n'
                            'Une clé primaire identifie une ligne de façon unique. Une clé étrangère référence une ligne '
                            'd’une autre table afin de relier les informations sans les recopier partout.'
                        ),
                        'exercise': 'Imagine une base de données d’école : propose deux tables, leurs colonnes et une relation entre elles.',
                    },
                    {
                        'title': 'Lire une table avec SELECT',
                        'duration': 20,
                        'objectives': ['Écrire une requête SELECT', 'Limiter les colonnes avec une liste de noms'],
                        'content': (
                            'SELECT choisit les colonnes à lire et FROM indique la table source. Par exemple, '
                            'SELECT nom, ville FROM apprenants; renvoie deux colonnes. L’astérisque sélectionne toutes '
                            'les colonnes, mais il vaut mieux ne demander que les données nécessaires.\n\n'
                            'Une requête ne modifie pas les données lorsqu’elle se limite à SELECT. Le point-virgule '
                            'termine souvent l’instruction.'
                        ),
                        'exercise': 'Écris une requête qui affiche seulement le nom et la ville de chaque apprenant.',
                    },
                ],
            },
            {
                'title': 'Filtrer et ordonner les résultats',
                'description': 'Affiche précisément les enregistrements utiles.',
                'lessons': [
                    {
                        'title': 'Filtrer avec WHERE',
                        'duration': 20,
                        'objectives': ['Ajouter une condition WHERE', 'Combiner des conditions simples avec AND'],
                        'content': (
                            'WHERE limite les lignes renvoyées par une requête. Les opérateurs =, <>, >, <, >= et <= '
                            'permettent de comparer des valeurs. BETWEEN sélectionne une plage et IN teste une liste '
                            'de valeurs.\n\n'
                            'AND exige que plusieurs conditions soient vraies ; OR accepte qu’au moins l’une le soit. '
                            'Utilise des parenthèses quand tu combines ces opérateurs pour rendre l’intention explicite.'
                        ),
                        'exercise': 'Écris une requête qui sélectionne les apprenants d’une ville donnée dont l’âge est supérieur à 18.',
                    },
                    {
                        'title': 'Trier et limiter les résultats',
                        'duration': 20,
                        'objectives': ['Trier avec ORDER BY', 'Choisir un ordre croissant ou décroissant'],
                        'content': (
                            'ORDER BY trie les lignes selon une ou plusieurs colonnes. ASC indique l’ordre croissant et '
                            'DESC l’ordre décroissant. Si aucun sens n’est indiqué, l’ordre croissant est généralement '
                            'utilisé.\n\n'
                            'Selon le moteur de base de données, LIMIT permet de réduire le nombre de lignes renvoyées. '
                            'Pour obtenir les personnes les plus récentes en premier, trie une date en ordre décroissant.'
                        ),
                        'exercise': 'Trie la liste des apprenants par nom, puis propose une variante qui affiche les plus récents en premier.',
                    },
                ],
            },
        ],
    },
]


def seed_learning_paths(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    CourseModule = apps.get_model('academy', 'CourseModule')
    CourseLesson = apps.get_model('academy', 'CourseLesson')
    database = schema_editor.connection.alias

    Formation.objects.using(database).filter(
        platform__in=['Cisco Networking Academy', 'IBM SkillsBuild', 'Microsoft Learn'],
    ).update(last_verified_at=timezone.now())

    for path in LEARNING_PATHS:
        formation, _ = Formation.objects.using(database).update_or_create(
            title=path['title'],
            platform='Jupython',
            defaults={
                'link': 'https://jupython.cd/academy/learn.html',
                'is_free': True,
                'description': 'Parcours conçu par Jupython. Les leçons, exercices et la progression sont disponibles dans ton espace.',
                'domain': path['domain'],
                'level': 'Débutant',
                'duration': path['duration'],
                'language': 'Français',
                'skills': path['skills'],
                'credential_info': path['credential_info'],
                'hosted_by_jupython': True,
                'last_verified_at': timezone.now(),
            },
        )
        for module_order, module_data in enumerate(path['modules'], start=1):
            module, _ = CourseModule.objects.using(database).update_or_create(
                formation=formation,
                order=module_order,
                defaults={
                    'title': module_data['title'],
                    'description': module_data['description'],
                },
            )
            for lesson_order, lesson_data in enumerate(module_data['lessons'], start=1):
                CourseLesson.objects.using(database).update_or_create(
                    module=module,
                    order=lesson_order,
                    defaults={
                        'title': lesson_data['title'],
                        'content': lesson_data['content'],
                        'exercise': lesson_data['exercise'],
                        'learning_objectives': lesson_data['objectives'],
                        'duration_minutes': lesson_data['duration'],
                    },
                )


class Migration(migrations.Migration):
    dependencies = [
        ('academy', '0005_formation_hosted_by_jupython_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_learning_paths, migrations.RunPython.noop),
    ]
