# Jupython — backend Django et PostgreSQL

API Django destinée au frontend Jupython. PostgreSQL est le seul moteur de base
de données pris en charge ; la base est fournie par Docker Compose.

## Prérequis

- Python 3.12
- Docker Desktop avec Docker Compose

## Installation locale (Windows)

1. Copier `.env.example` vers `.env`, puis définir une `SECRET_KEY` unique et un
   `DB_PASSWORD` fort. Ajouter le client Google si la connexion Google est utilisée.
2. Créer et activer l’environnement Python, puis installer les dépendances :

   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Démarrer PostgreSQL et créer le schéma :

   ```powershell
   docker compose up -d postgres
   python manage.py migrate
   ```

4. Créer un compte administrateur et lancer Django :

   ```powershell
   python manage.py createsuperuser
   python manage.py runserver
   ```

Django lancé sur Windows se connecte à `localhost:5432`. Si Django est lancé
dans un conteneur du même réseau Compose, définir `DB_HOST=postgres`.
`DB_PORT` est le port publié sur l'hôte (5432 par défaut).

## Configuration

Les paramètres sont chargés depuis `.env` : `SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`,
`GOOGLE_CLIENT_ID` et `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
En production, désactiver `DEBUG`, fournir une clé secrète et configurer
explicitement les hôtes et origines autorisés.

Pour activer la connexion Google, crée un identifiant OAuth de type
**Application Web** dans Google Cloud Console, ajoute l'origine exacte du site
(en local : `http://127.0.0.1:8000`) aux origines JavaScript autorisées, puis
inscris son identifiant dans `GOOGLE_CLIENT_ID` du fichier `.env`. Redémarre
Django après cette modification. Sans identifiant configuré, le bouton Google
reste désactivé avec le même libellé sur les pages connexion et inscription.

Les API de profil, d'inscription aux formations et de certifications exigent
un jeton JWT. Les tentatives de connexion sont limitées à cinq par minute et la
déconnexion révoque le jeton de renouvellement. Le jeton d'accès est renouvelé
automatiquement pendant l'utilisation du site. La session reste enregistrée
dans le navigateur et se prolonge à chaque renouvellement ; après 30 jours
d'inactivité, l'utilisateur devra se reconnecter. La déconnexion n'a lieu que
sur demande de l'utilisateur ou si le jeton de renouvellement a expiré ou a été
révoqué.

Le catalogue Academy réunit des parcours enseignés sur Jupython et des cours
référencés chez leurs fournisseurs officiels. Exécute `python manage.py migrate`
après la mise à jour. Les leçons Jupython, les exercices et leur progression sont
hébergés sur le site et enregistrés individuellement pour chaque apprenant. Pour
les cours externes, Jupython garde l'inscription et l'avancement déclaré, tandis
que le fournisseur gère le contenu et les certificats. Les certificats externes
envoyés au profil restent en attente jusqu'à vérification par un administrateur ;
un badge de cours n'est pas présenté comme une certification professionnelle.

Les informations des cours externes ont une date de vérification dans le
catalogue. Depuis l'administration, filtre « À revérifier (> 30 jours) » et
marque un cours revu après avoir contrôlé son lien, sa langue, son prix et son
attestation chez le fournisseur. Les plateformes n'exposent pas toutes un
catalogue synchronisable ; les changements doivent donc être confirmés avant
d'être publiés sur Jupython.

Les parcours Jupython couvrent plusieurs niveaux. Les parcours intermédiaires
indiquent leurs prérequis et un projet de sortie ; ils sont conçus autour de
pratiques professionnelles en API Django, réponse défensive aux incidents,
analyse de données avec Python/SQL et livraison DevOps. Leur suivi et les
exercices sont disponibles dans la page de chaque parcours. L'inscription à un
cours Jupython est unique et conserve la progression entre les connexions. Les
leçons d'un module doivent être terminées, puis son test réussi (au moins deux
bonnes réponses sur trois) pour débloquer le module suivant. Les leçons restent
consultables en aperçu avant connexion ; le contenu complet, les objectifs et
les exercices nécessitent un compte connecté. Une leçon marquée lue et terminée
apparaît en vert et sa progression est conservée. L'inscription au parcours
permet d'enregistrer la progression et de passer les tests, qui peuvent être
retentés.
Chaque module comprend aussi un schéma visuel local qui résume ses leçons,
son test et l'étape suivante, sans dépendance à un service vidéo externe. La
page d'apprentissage présente le parcours en étapes, ouvre la prochaine leçon
à continuer, et permet de replier les leçons déjà lues pour se concentrer sur
la suite. Les mini-défis et les retours de progression accompagnent chaque
étape.

Chaque membre peut modifier son nom/pseudo public, sa biographie et sa photo
depuis « Profil ». Les profils publics ne renvoient que ces trois informations ;
les e-mails, universités, formations et certifications restent privés. Les
photos sont limitées aux formats JPEG, PNG et WebP, à 5 Mo et 4096 pixels par
côté. En production, configure le serveur web ou le stockage de fichiers pour
servir `/media/` depuis `MEDIA_ROOT` et conserver ce répertoire durablement.
Le serveur web doit également servir `/images/` depuis
`frontend/frontend/images/` pour afficher le logo de la plateforme.

Le fichier `db.sqlite3` éventuellement présent n'est plus utilisé ni migré
automatiquement. Il est conservé pour éviter toute perte de données.
