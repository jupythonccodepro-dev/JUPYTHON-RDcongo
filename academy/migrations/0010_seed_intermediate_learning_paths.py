from django.db import migrations
from django.utils import timezone


PATHS = [
    {
        'title': 'Développer une API professionnelle avec Django REST',
        'domain': 'Backend et API',
        'duration': '12 à 16 heures',
        'skills': ['Django', 'Django REST Framework', 'API REST', 'JWT', 'Tests automatisés', 'Sécurité API'],
        'prerequisites': 'Connaître les bases de Python, les fonctions, les classes, Git et les requêtes HTTP. Le cours « Python pratique : les fondamentaux » est un bon préalable.',
        'project_outcome': 'Projet final : concevoir une API de gestion de tâches avec comptes utilisateurs, permissions, validation, tests automatisés et documentation des routes.',
        'modules': [
            {
                'title': 'Concevoir une API et son modèle de données',
                'description': 'Passe des besoins d’un produit à des ressources HTTP et à un schéma de données cohérent.',
                'lessons': [
                    {
                        'title': 'Modéliser les ressources et les contrats HTTP',
                        'duration': 45,
                        'objectives': ['Découper un besoin en ressources API', 'Choisir les méthodes et statuts HTTP adaptés'],
                        'content': (
                            'Une API REST expose des ressources identifiées par des URL, par exemple /api/tasks/ et '
                            '/api/tasks/42/. GET lit, POST crée, PUT remplace, PATCH modifie partiellement et DELETE '
                            'supprime. Les réponses doivent utiliser des statuts explicites : 200 pour une lecture ou '
                            'modification réussie, 201 pour une création, 204 pour une suppression sans corps, 400 pour '
                            'une entrée invalide, 401 pour une absence d’authentification et 403 pour un refus d’accès.\n\n'
                            'Avant de coder, écris le contrat de chaque route : méthode, URL, champs acceptés, réponse et '
                            'erreurs possibles. Évite de révéler si un compte d’un autre utilisateur existe quand une '
                            'route doit simplement être inaccessible.'
                        ),
                        'exercise': 'Rédige le contrat HTTP de trois routes pour créer une tâche, lister les tâches de l’utilisateur et terminer une tâche. Justifie chaque statut.',
                    },
                    {
                        'title': 'Construire les modèles et les migrations Django',
                        'duration': 50,
                        'objectives': ['Transformer une entité métier en modèle Django', 'Générer et tester une migration'],
                        'content': (
                            'Un modèle Django décrit la structure persistée d’une entité. Pour une tâche, on peut prévoir '
                            'un titre, une description, un état, des horodatages et une clé étrangère vers son propriétaire. '
                            'Les choix d’état doivent être bornés et les contraintes importantes garanties aussi en base, '
                            'par exemple l’unicité d’un numéro parmi les éléments d’un même propriétaire.\n\n'
                            'Après un changement de modèle, makemigrations génère une migration ; migrate l’applique. '
                            'Une migration partagée doit être relue et testée sur une base propre : elle fait partie du '
                            'code de l’application et doit pouvoir être rejouée dans les déploiements.'
                        ),
                        'exercise': 'Dessine le modèle Task avec son propriétaire, trois états autorisés et une règle empêchant les titres vides. Décris les migrations nécessaires pour ajouter un champ priorité.',
                    },
                ],
            },
            {
                'title': 'Implémenter, valider et sécuriser les endpoints',
                'description': 'Expose le modèle avec des réponses prévisibles et des règles d’accès par propriétaire.',
                'lessons': [
                    {
                        'title': 'Sérialise les données et valide les entrées',
                        'duration': 55,
                        'objectives': ['Définir les champs exposés par un serializer', 'Retourner une erreur de validation exploitable'],
                        'content': (
                            'Un serializer transforme des objets Python en JSON et valide les données entrantes. Déclare '
                            'explicitement les champs publics plutôt que d’exposer automatiquement tous les champs du '
                            'modèle : identifiants internes, propriétaire, dates d’audit ou données privées ne doivent pas '
                            'devenir modifiables sans intention.\n\n'
                            'La validation doit contrôler le type, la longueur, les choix autorisés et les invariants '
                            'métier. Les erreurs doivent identifier le champ concerné sans renvoyer de trace technique, '
                            'de secret ou de données d’un autre compte.'
                        ),
                        'exercise': 'Définis les entrées acceptées pour créer ou mettre à jour une tâche et les erreurs à renvoyer pour un titre vide, un état inconnu ou un champ propriétaire envoyé par le client.',
                    },
                    {
                        'title': 'Filtrer par utilisateur et appliquer les permissions',
                        'duration': 55,
                        'objectives': ['Restreindre une queryset à l’utilisateur authentifié', 'Distinguer authentification et autorisation'],
                        'content': (
                            'Authentifier un appel répond à « qui fait la requête ? » ; l’autorisation répond à « peut-il '
                            'agir sur cet objet ? ». Pour un espace personnel, le queryset des tâches doit être filtré '
                            'avec request.user. L’identifiant d’objet fourni dans l’URL ne constitue jamais une preuve '
                            'de propriété.\n\n'
                            'À la création, attribue le propriétaire côté serveur depuis request.user, et non depuis le '
                            'JSON client. Vérifie aussi les actions de liste, détail, modification et suppression ; une '
                            'route de détail protégée ne compense pas une liste qui renvoie les éléments de tous les comptes.'
                        ),
                        'exercise': 'Écris les tests d’autorisation pour deux comptes Alice et Bob : Bob ne doit ni voir, ni modifier, ni supprimer la tâche d’Alice, même s’il connaît son identifiant.',
                    },
                ],
            },
            {
                'title': 'Tester et préparer la livraison',
                'description': 'Protège le contrat de l’API contre les régressions puis prépare une mise en production.',
                'lessons': [
                    {
                        'title': 'Tester les succès, les erreurs et l’isolation',
                        'duration': 60,
                        'objectives': ['Tester une API avec le client de test REST', 'Couvrir les cas d’accès refusé'],
                        'content': (
                            'Un test d’API vérifie le comportement observable : code HTTP, forme de la réponse, persistance '
                            'et permissions. Couvre le chemin heureux mais aussi les données invalides, le client non '
                            'authentifié, l’utilisateur qui tente d’accéder à un objet étranger et les doublons.\n\n'
                            'Les tests doivent être indépendants et créer leurs propres données. Préfère des assertions '
                            'sur les champs utiles à un instantané complet qui casse au moindre changement sans rapport. '
                            'Lance les tests après chaque changement de schéma et avant chaque livraison.'
                        ),
                        'exercise': 'Écris un plan de tests API couvrant création, liste personnelle, mise à jour, suppression, JSON invalide, 401 et accès d’un autre utilisateur.',
                    },
                    {
                        'title': 'Gérer les secrets, les limites et la documentation',
                        'duration': 50,
                        'objectives': ['Garder les clés secrètes hors du dépôt', 'Documenter les paramètres, erreurs et limites'],
                        'content': (
                            'Ne place pas SECRET_KEY, mots de passe de base ou clés de fournisseur dans Git, une image '
                            'Docker ou les réponses de l’API. Injecte-les depuis l’environnement de déploiement, utilise '
                            'une configuration distincte par environnement et renouvelle tout secret qui a été exposé.\n\n'
                            'Une API publique doit limiter les tentatives sensibles, prévoir des délais raisonnables et '
                            'documenter authentification, routes, champs, erreurs et pagination. Avant le déploiement, '
                            'vérifie DEBUG désactivé, HTTPS, hôtes autorisés, migrations appliquées et journaux sans '
                            'jeton ni mot de passe.'
                        ),
                        'exercise': 'Prépare une checklist de lancement de ton API : variables secrètes, HTTPS, limitations, permissions, migrations, erreurs JSON et documentation.',
                    },
                ],
            },
        ],
    },
    {
        'title': 'Cybersécurité défensive : analyser et répondre aux incidents',
        'domain': 'Cybersécurité',
        'duration': '10 à 14 heures',
        'skills': ['Analyse de journaux', 'Triage d’alertes', 'Réponse aux incidents', 'Durcissement', 'Gestion des vulnérabilités'],
        'prerequisites': 'Avoir des notions de réseaux IP, DNS, systèmes Linux ou Windows et lignes de commande. Le parcours se limite à la défense de systèmes autorisés.',
        'project_outcome': 'Projet final : analyser un scénario de phishing et d’accès suspect, reconstituer une chronologie à partir de journaux fournis et rédiger un rapport de réponse défensive.',
        'modules': [
            {
                'title': 'Comprendre les traces et les signaux',
                'description': 'Apprends à contextualiser des alertes plutôt qu’à réagir à un seul événement isolé.',
                'lessons': [
                    {
                        'title': 'Lire des journaux d’authentification et de réseau',
                        'duration': 50,
                        'objectives': ['Identifier les champs courants d’un journal', 'Construire une chronologie à partir d’événements'],
                        'content': (
                            'Un journal utile contient un horodatage avec fuseau, une source, une action, un résultat et '
                            'un identifiant de corrélation. Les journaux d’authentification peuvent révéler des échecs '
                            'répétés, une connexion inhabituelle ou un nouveau facteur ; les journaux DNS et réseau aident '
                            'à identifier les systèmes concernés.\n\n'
                            'Un événement isolé est rarement une preuve. Normalise les horodatages, distingue les comptes '
                            'humains des services, établis ce qui est attendu et conserve les données originales. Ne '
                            'modifie pas les journaux de production pendant une enquête.'
                        ),
                        'exercise': 'À partir d’une séquence fictive de connexions réussies et échouées, établis la chronologie, les comptes touchés et les informations encore manquantes.',
                    },
                    {
                        'title': 'Trier une alerte de sécurité',
                        'duration': 50,
                        'objectives': ['Évaluer l’impact, la portée et l’urgence', 'Documenter des hypothèses vérifiables'],
                        'content': (
                            'Le triage commence par vérifier la source et la qualité du signal, identifier l’actif et le '
                            'compte concernés, mesurer l’impact possible et chercher des événements liés. Priorise selon '
                            'la criticité de l’actif, l’exposition, les privilèges et la présence d’une activité encore '
                            'en cours, pas uniquement selon la couleur attribuée par un outil.\n\n'
                            'Documente les faits séparément des hypothèses. Chaque recherche doit répondre à une question '
                            'et laisser une trace reproductible. Si les preuves sont insuffisantes, formule clairement '
                            'ce qui manque et escalade selon la procédure de l’organisation.'
                        ),
                        'exercise': 'Crée une fiche de triage pour une alerte de connexion depuis un nouvel emplacement : actif, faits observés, hypothèses, impact, prochaine vérification et décision d’escalade.',
                    },
                ],
            },
            {
                'title': 'Conduire une réponse à incident',
                'description': 'Contiens les risques sans détruire les éléments utiles à l’enquête.',
                'lessons': [
                    {
                        'title': 'Préserver les preuves et limiter l’impact',
                        'duration': 55,
                        'objectives': ['Suivre une procédure d’escalade', 'Choisir des mesures de confinement proportionnées'],
                        'content': (
                            'Une réponse structurée comprend préparation, détection, analyse, confinement, éradication, '
                            'rétablissement et retour d’expérience. L’ordre précis dépend du risque et du plan de '
                            'l’organisation. Isole une machine ou révoque une session uniquement selon les procédures et '
                            'avec l’autorité prévue.\n\n'
                            'Consigne les décisions, l’heure, la personne qui les prend et leurs conséquences. Préserve '
                            'les journaux, identifiants d’incident et éléments nécessaires à l’analyse. Ne lance pas '
                            'd’outils sur un système réel sans permission explicite.'
                        ),
                        'exercise': 'Établis un plan de confinement pour un compte supposé compromis, avec mesures autorisées, propriétaire de chaque action et preuves à préserver.',
                    },
                    {
                        'title': 'Enquêter sur un message de phishing',
                        'duration': 55,
                        'objectives': ['Examiner des en-têtes et indicateurs sans ouvrir un lien suspect', 'Déterminer qui prévenir et quoi bloquer'],
                        'content': (
                            'Examine le message dans un environnement prévu à cet effet. Les champs From, Reply-To, '
                            'Return-Path, SPF, DKIM et DMARC donnent des indices sur l’authentification et l’acheminement, '
                            'mais un résultat positif ne garantit pas à lui seul que le message est légitime.\n\n'
                            'Relève les domaines, horaires et destinataires concernés sans ouvrir la pièce jointe ou le '
                            'lien sur un poste de travail. Cherche des messages identiques et des interactions déjà '
                            'signalées. Le blocage d’un domaine ou la communication aux utilisateurs doit suivre le '
                            'processus de l’organisation.'
                        ),
                        'exercise': 'Prépare un rapport d’analyse d’un courriel fictif : indices observés, destinataires à vérifier, mesures de précaution et communication à envoyer.',
                    },
                ],
            },
            {
                'title': 'Réduire le risque et rendre compte',
                'description': 'Relie les constats à des actions de sécurité mesurables.',
                'lessons': [
                    {
                        'title': 'Prioriser les correctifs et les accès',
                        'duration': 45,
                        'objectives': ['Évaluer une vulnérabilité par exposition et impact', 'Appliquer le principe du moindre privilège'],
                        'content': (
                            'La gravité technique aide à comparer les failles mais ne remplace pas le contexte : exposition '
                            'Internet, données accessibles, exploit disponible, contrôles compensatoires et criticité métier '
                            'influencent la priorité. Un inventaire d’actifs exact et une procédure de correction testée '
                            'réduisent le risque plus sûrement qu’une mise à jour précipitée sans retour arrière.\n\n'
                            'Le moindre privilège donne à chaque compte les droits nécessaires pour sa tâche, pendant la '
                            'durée utile. Supprime les comptes inutilisés, protège les comptes d’administration et revois '
                            'régulièrement les accès.'
                        ),
                        'exercise': 'Classe trois vulnérabilités fictives selon leur risque métier et propose un correctif, un responsable, une échéance et un contrôle après correction.',
                    },
                    {
                        'title': 'Rédiger un rapport de fin d’incident',
                        'duration': 45,
                        'objectives': ['Séparer faits et incertitudes', 'Transformer les leçons apprises en actions vérifiables'],
                        'content': (
                            'Un rapport d’incident concis contient résumé exécutif, portée connue, chronologie, impact, '
                            'mesures appliquées, incertitudes restantes et recommandations. Protège les informations '
                            'personnelles et les détails opérationnels qui ne doivent pas être largement diffusés.\n\n'
                            'Une recommandation utile a un responsable, une échéance, un critère de réussite et une preuve '
                            'de validation. Le retour d’expérience vise à améliorer les contrôles et procédures, pas à '
                            'blâmer une personne.'
                        ),
                        'exercise': 'Rédige le plan du rapport final du projet et transforme deux constats en actions mesurables avec critères de validation.',
                    },
                ],
            },
        ],
    },
    {
        'title': 'Data Analytics : transformer un jeu de données en décision',
        'domain': 'Data et analytique',
        'duration': '12 à 16 heures',
        'skills': ['Python', 'Pandas', 'SQL', 'Qualité des données', 'Visualisation', 'Communication des résultats'],
        'prerequisites': 'Connaître les bases de Python et SQL. Une familiarité avec les tableaux et les fichiers CSV est utile.',
        'project_outcome': 'Projet final : nettoyer un jeu de ventes fictif, calculer des indicateurs fiables, produire trois visualisations et rédiger une recommandation à destination d’une équipe métier.',
        'modules': [
            {
                'title': 'Inspecter et préparer des données',
                'description': 'Évalue la qualité et transforme un fichier brut sans masquer les problèmes.',
                'lessons': [
                    {
                        'title': 'Définir une question avant d’analyser',
                        'duration': 45,
                        'objectives': ['Transformer un besoin métier en question mesurable', 'Choisir une unité d’analyse et des indicateurs'],
                        'content': (
                            'Une analyse commence par une décision à éclairer, pas par un graphique. Reformule le besoin '
                            'en question vérifiable, précise la population et la période, puis définis l’unité d’analyse '
                            '(par exemple une commande, une journée ou un client).\n\n'
                            'Un indicateur doit avoir une définition stable, une unité, une période et une source. Le '
                            'chiffre d’affaires peut signifier montant brut, montant après remises ou montant net des '
                            'annulations ; documente le choix. Évite de confondre corrélation et causalité.'
                        ),
                        'exercise': 'Pour la question « pourquoi les ventes baissent-elles ? », propose trois questions mesurables, leur période et l’indicateur associé.',
                    },
                    {
                        'title': 'Contrôler un CSV avec Pandas',
                        'duration': 55,
                        'objectives': ['Inspecter colonnes et types', 'Repérer valeurs manquantes, doublons et formats incohérents'],
                        'content': (
                            'Avec Pandas, read_csv charge un fichier en DataFrame. Commence par afficher quelques lignes, '
                            'la forme du tableau, les noms de colonnes, les types et les valeurs manquantes. Contrôle '
                            'ensuite les doublons de clé, les dates impossibles, les unités mélangées et les valeurs '
                            'hors du domaine attendu.\n\n'
                            'Ne supprime pas automatiquement une ligne invalide. Distingue donnée absente, inconnue, '
                            'non applicable et erreur de saisie. Garde une copie de la source et consigne chaque règle '
                            'de nettoyage afin que l’analyse puisse être rejouée.'
                        ),
                        'exercise': 'Décris un audit de qualité pour un CSV de ventes : quelles colonnes contrôles-tu, quelles anomalies cherches-tu et comment conserves-tu une trace des corrections ?',
                    },
                ],
            },
            {
                'title': 'Analyser et vérifier les résultats',
                'description': 'Combine SQL et Python pour calculer des indicateurs reproductibles.',
                'lessons': [
                    {
                        'title': 'Joindre et agréger des tables SQL',
                        'duration': 55,
                        'objectives': ['Choisir une jointure selon la question', 'Vérifier le grain avant un agrégat'],
                        'content': (
                            'JOIN relie des lignes sur une clé. INNER JOIN ne conserve que les correspondances ; '
                            'LEFT JOIN garde aussi les lignes de gauche sans correspondance. Avant toute somme, vérifie '
                            'la cardinalité : une jointure un-à-plusieurs peut multiplier les lignes et gonfler un total.\n\n'
                            'GROUP BY calcule une mesure par groupe, avec COUNT, SUM, AVG, MIN ou MAX. Filtre les lignes '
                            'avant ou après l’agrégation selon la question et compare les totaux avant et après la jointure '
                            'pour repérer les duplications.'
                        ),
                        'exercise': 'À partir de tables fictives commandes et clients, écris le plan SQL permettant d’obtenir le montant total par région et explique comment tu détecterais une jointure qui double les ventes.',
                    },
                    {
                        'title': 'Calculer des indicateurs fiables avec Pandas',
                        'duration': 55,
                        'objectives': ['Créer des colonnes dérivées sans modifier la source', 'Comparer les résultats à des totaux de contrôle'],
                        'content': (
                            'Pandas permet de filtrer un DataFrame, créer une colonne calculée et regrouper par catégorie '
                            'avec groupby. Convertis les dates et nombres explicitement, choisis une règle pour les valeurs '
                            'manquantes et garde des étapes de transformation nommées.\n\n'
                            'Un indicateur fiable se contrôle : comparer le nombre de lignes, les totaux connus et les '
                            'résultats d’une seconde méthode réduit les erreurs silencieuses. Conserve un échantillon '
                            'de lignes source pour expliquer un chiffre et note les hypothèses de calcul.'
                        ),
                        'exercise': 'Définis les contrôles qui valident un indicateur de ventes nettes calculé avec Pandas après retrait des commandes annulées et application des remises.',
                    },
                ],
            },
            {
                'title': 'Communiquer une recommandation',
                'description': 'Choisis les visualisations qui répondent à la question et expliquent les limites.',
                'lessons': [
                    {
                        'title': 'Choisir une visualisation sans induire en erreur',
                        'duration': 45,
                        'objectives': ['Associer un graphique à une comparaison ou une évolution', 'Étiqueter unités et périodes'],
                        'content': (
                            'Un graphique en lignes convient souvent à une évolution temporelle, des barres à une '
                            'comparaison de catégories et un nuage de points à une relation entre deux mesures. Évite '
                            'les axes tronqués qui exagèrent un écart et les palettes où la couleur est le seul moyen '
                            'de distinguer une valeur.\n\n'
                            'Donne un titre informatif, indique l’unité et la période et cite la source. Chaque graphique '
                            'doit répondre à une question. Un tableau de bord trop chargé empêche le lecteur de repérer '
                            'les résultats importants.'
                        ),
                        'exercise': 'Choisis trois graphiques pour comparer les ventes mensuelles par région, justifie-les et indique titre, unité, période et limites.',
                    },
                    {
                        'title': 'Présenter les résultats avec leurs limites',
                        'duration': 45,
                        'objectives': ['Distinguer observation et recommandation', 'Expliquer les limites et prochaines vérifications'],
                        'content': (
                            'Une recommandation efficace relie un résultat à une décision possible et précise le niveau '
                            'de confiance. Présente d’abord la question, puis les faits contrôlés, l’interprétation, '
                            'l’action suggérée et la manière d’en mesurer l’effet.\n\n'
                            'Mentionne la couverture du jeu de données, les biais possibles, les valeurs exclues et les '
                            'hypothèses. Un résultat exploratoire n’établit pas à lui seul une causalité. Une expérience '
                            'ou une collecte complémentaire peut être nécessaire avant une décision coûteuse.'
                        ),
                        'exercise': 'Rédige une synthèse de cinq phrases à destination d’un responsable : résultat, preuve, recommandation, limite et prochain contrôle.',
                    },
                ],
            },
        ],
    },
    {
        'title': 'DevOps : automatiser les tests et livrer une application',
        'domain': 'DevOps et Cloud',
        'duration': '12 à 16 heures',
        'skills': ['Git', 'CI/CD', 'Docker', 'Variables d’environnement', 'Déploiement', 'Surveillance'],
        'prerequisites': 'Savoir utiliser la ligne de commande, Git et lancer une application web. Les déploiements cloud peuvent avoir des coûts distincts.',
        'project_outcome': 'Projet final : préparer une application web pour la livraison avec tests automatisés, image Docker, configuration par variables d’environnement, procédure de déploiement et vérification de santé.',
        'modules': [
            {
                'title': 'Structurer le code et automatiser les vérifications',
                'description': 'Construis un flux de livraison répétable avant d’ajouter l’infrastructure.',
                'lessons': [
                    {
                        'title': 'Organiser les branches et les changements Git',
                        'duration': 45,
                        'objectives': ['Créer des commits cohérents', 'Utiliser une revue avant intégration'],
                        'content': (
                            'Un commit doit représenter un changement compréhensible et réversible. Vérifie le diff avant '
                            'de valider, n’ajoute pas de secrets ni de fichiers générés inutiles, et écris un message '
                            'qui décrit l’intention.\n\n'
                            'Une branche courte isole une modification. La revue examine la correction, les tests, les '
                            'effets de bord et la documentation ; elle ne remplace pas l’automatisation. Résous les '
                            'conflits en comprenant les deux changements, puis relance les vérifications.'
                        ),
                        'exercise': 'Propose une séquence Git pour ajouter une route à une application : branche, commits, revue, tests et fusion.',
                    },
                    {
                        'title': 'Construire une pipeline de tests',
                        'duration': 55,
                        'objectives': ['Définir des étapes de CI déterministes', 'Bloquer une livraison lorsque les tests échouent'],
                        'content': (
                            'L’intégration continue exécute les mêmes contrôles à chaque changement : installation de '
                            'dépendances verrouillées, analyse statique, tests et éventuellement construction d’un '
                            'artefact. Une étape doit échouer clairement si un contrôle échoue ; ne transforme pas une '
                            'erreur en succès apparent.\n\n'
                            'Sépare les secrets du code et ne les expose pas dans les logs. Les tests doivent être '
                            'reproductibles avec des versions de dépendances maîtrisées. Garde les étapes rapides au '
                            'début et réserve les tests longs à un niveau adapté.'
                        ),
                        'exercise': 'Dessine une pipeline CI pour une application Django : étapes, conditions d’échec, secrets nécessaires et artefact produit.',
                    },
                ],
            },
            {
                'title': 'Conteneuriser sans cacher les risques',
                'description': 'Prépare une image exécutable de façon reproductible et configure-la par environnement.',
                'lessons': [
                    {
                        'title': 'Construire une image Docker maîtrisée',
                        'duration': 55,
                        'objectives': ['Distinguer image et conteneur', 'Réduire le contexte de build et éviter les secrets dans l’image'],
                        'content': (
                            'Une image est un modèle immuable ; un conteneur est une instance en exécution. Le Dockerfile '
                            'décrit les étapes de construction et le contexte envoyé au moteur détermine quels fichiers '
                            'sont accessibles. Un .dockerignore évite d’envoyer environnements virtuels, caches, bases '
                            'locales et fichiers contenant des secrets.\n\n'
                            'Utilise une image de base maintenue, installe les dépendances nécessaires et exécute le '
                            'processus avec des privilèges minimaux. Ne copie pas un fichier .env dans l’image et ne '
                            'suppose pas qu’un conteneur garde ses fichiers après remplacement.'
                        ),
                        'exercise': 'Relis un Dockerfile fictif et repère les secrets copiés, l’utilisateur root, les fichiers inutiles et les dépendances non verrouillées. Propose les corrections.',
                    },
                    {
                        'title': 'Configurer l’application et ses services',
                        'duration': 50,
                        'objectives': ['Injecter la configuration au démarrage', 'Comprendre les dépendances entre application et base'],
                        'content': (
                            'L’application doit lire la configuration depuis l’environnement d’exécution. Une base de '
                            'données a son propre cycle de vie et son stockage persistant ; son adresse, ses identifiants '
                            'et les paramètres de connexion varient selon l’environnement.\n\n'
                            'Un ordre de démarrage n’assure pas qu’une base est prête à accepter les connexions. Prévois '
                            'des contrôles de disponibilité et une stratégie explicite pour les migrations. Les données '
                            'persistantes doivent être sauvegardées et testées en restauration.'
                        ),
                        'exercise': 'Décris les services, variables et volumes nécessaires pour exécuter une application web avec une base PostgreSQL en développement et en production.',
                    },
                ],
            },
            {
                'title': 'Livrer, surveiller et revenir en arrière',
                'description': 'Définis un déploiement observable et une récupération maîtrisée.',
                'lessons': [
                    {
                        'title': 'Déployer avec des contrôles de santé',
                        'duration': 50,
                        'objectives': ['Distinguer disponibilité et état du processus', 'Vérifier le service après déploiement'],
                        'content': (
                            'Un contrôle de santé doit indiquer si le service peut réellement traiter une requête, sans '
                            'exposer de secrets ou de diagnostics détaillés au public. La disponibilité d’un processus '
                            'ne garantit pas celle de ses dépendances.\n\n'
                            'Un déploiement prudent vérifie l’artefact, applique les changements compatibles, observe '
                            'les erreurs et le temps de réponse, puis poursuit ou s’arrête selon des critères connus. '
                            'Prévois une procédure de retour arrière et sache quelles migrations de données sont '
                            'réversibles avant de remplacer une version.'
                        ),
                        'exercise': 'Établis un plan de mise en production avec vérifications avant/après, seuils d’arrêt et étapes de retour arrière.',
                    },
                    {
                        'title': 'Lire des journaux et préparer les sauvegardes',
                        'duration': 50,
                        'objectives': ['Journaliser un identifiant de requête sans donnée sensible', 'Définir un test de restauration'],
                        'content': (
                            'Les journaux structurés indiquent l’heure, le niveau, le service et un identifiant de '
                            'requête utile à la corrélation. N’y écris jamais un mot de passe, une clé, un jeton ou le '
                            'contenu privé d’une requête. Les mesures de performance complètent les journaux en révélant '
                            'latence, erreurs et saturation.\n\n'
                            'Une sauvegarde non restaurée n’est pas une stratégie vérifiée. Définis fréquence, durée de '
                            'rétention, protection des accès et objectif de restauration. Organise un test de restauration '
                            'dans un environnement isolé et documente le temps réellement nécessaire.'
                        ),
                        'exercise': 'Écris une checklist d’exploitation pour ton projet : journaux sans secrets, métriques, alertes, fréquence de sauvegarde et exercice de restauration.',
                    },
                ],
            },
        ],
    },
]


def seed_intermediate_paths(apps, schema_editor):
    Formation = apps.get_model('academy', 'Formation')
    CourseModule = apps.get_model('academy', 'CourseModule')
    CourseLesson = apps.get_model('academy', 'CourseLesson')
    database = schema_editor.connection.alias

    for path in PATHS:
        formation, _ = Formation.objects.using(database).update_or_create(
            title=path['title'],
            platform='Jupython',
            defaults={
                'link': 'https://jupython.cd/academy/learn.html',
                'is_free': True,
                'description': (
                    f"Parcours intermédiaire orienté pratique. Prérequis : {path['prerequisites']} "
                    f"Projet de sortie : {path['project_outcome']}"
                ),
                'domain': path['domain'],
                'level': 'Intermédiaire',
                'duration': path['duration'],
                'language': 'Français',
                'skills': path['skills'],
                'credential_info': (
                    'Parcours et progression suivis sur Jupython. La validation indique que les leçons ont été suivies ; '
                    'elle ne constitue pas une certification professionnelle.'
                ),
                'hosted_by_jupython': True,
                'last_verified_at': timezone.now(),
                'prerequisites': path['prerequisites'],
                'project_outcome': path['project_outcome'],
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
        ('academy', '0009_formation_prerequisites_formation_project_outcome'),
    ]

    operations = [
        migrations.RunPython(seed_intermediate_paths, migrations.RunPython.noop),
    ]
