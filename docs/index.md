# School Manager

**School Manager** est une application web Django qui centralise la gestion des écoles d'un réseau : fiches d'établissement, documents associés et comptes utilisateurs avec rôles.

Elle expose à la fois une **interface web** (pages HTML rendues côté serveur) et une **API REST** documentée (OpenAPI / Swagger).

## Fonctionnalités principales

| Domaine | Ce qui est fourni |
| --- | --- |
| Authentification | Inscription, connexion, déconnexion via pages web **et** via API à jeton (`/api/auth/…`). |
| Rôles | `admin` (gestion complète) et `user` (consultation). Un compte créé par inscription est toujours `user`. |
| Sécurité des mots de passe | Hachage **Argon2** (mécanismes natifs Django), validateurs de robustesse, aucun mot de passe en clair. |
| Écoles (CRUD) | Création, consultation, modification, suppression ; recherche, tri et pagination. |
| Documents | Upload de fichiers rattachés à une école, validation du type et de la taille, téléchargement authentifié. |
| Base de données | PostgreSQL 16, migrations versionnées, commande `wait_for_db` et endpoint `/api/health/`. |
| Qualité | 107 tests unitaires, couverture de 98 %, lint Ruff, intégration continue GitHub Actions. |
| Exploitation | Image Docker multi-étapes non-root, Gunicorn, WhiteNoise, `docker-compose.yml` (app + PostgreSQL). |

## Démarrage express

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

L'application est alors disponible sur [http://localhost:8000](http://localhost:8000) et la documentation interactive de l'API sur [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/).

## Pile technique

- Python 3.13, Django 5.2 LTS, Django REST Framework 3.18
- PostgreSQL 16 (pilote `psycopg` 3)
- drf-spectacular (schéma OpenAPI 3)
- Gunicorn + WhiteNoise
- MkDocs Material pour cette documentation

## Organisation de la documentation

- [Installation](installation.md) : prérequis et mise en route locale ou Docker.
- [Configuration](configuration.md) : toutes les variables d'environnement.
- [Architecture](architecture.md) : découpage du code et choix de conception.
- [Fonctionnalités](fonctionnalites/authentification.md) : authentification, écoles, fichiers, API.
- [Base de données](base-de-donnees.md) : PostgreSQL, migrations et vérifications.
- [Tests](tests.md) : exécution et résultats.
- [Déploiement](deploiement/docker.md) : Docker et mise en production.
- [Dépendances](dependances.md) : contenu de `requirements.txt`.
