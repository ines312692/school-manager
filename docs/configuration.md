# Configuration

Toute la configuration passe par des **variables d'environnement**, conformément aux principes *12-factor*. Le fichier `.env` (à créer depuis `.env.example`) est lu au démarrage par `config/env.py`, sans jamais écraser une variable déjà présente dans l'environnement.

## Modules de paramètres

| Module | Usage | Sélection |
| --- | --- | --- |
| `config.settings.base` | Socle commun | importé par les autres |
| `config.settings.development` | Développement local (`DEBUG` actif par défaut) | défaut de `manage.py` |
| `config.settings.test` | Tests (hachage rapide, cache factice) | `--settings=config.settings.test` |
| `config.settings.production` | Production (en-têtes de sécurité, JSON uniquement pour l'API) | défaut de `wsgi.py`, `asgi.py` et de l'image Docker |

## Variables Django

| Variable | Défaut | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | clé de dev | **Obligatoire en production.** Clé longue et aléatoire. |
| `DJANGO_DEBUG` | `False` (`True` en dev) | Mode débogage. Jamais en production. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Noms d'hôte autorisés, séparés par des virgules. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | vide | Origines de confiance (`https://ecoles.example.com`). |
| `DJANGO_MEDIA_ROOT` | `./media` | Répertoire de stockage des fichiers uploadés. |
| `DJANGO_LOG_LEVEL` | `INFO` | Niveau de journalisation. |

## Variables de sécurité (production)

| Variable | Défaut | Description |
| --- | --- | --- |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` | Redirige HTTP vers HTTPS (sauf `/api/health/`). |
| `DJANGO_SECURE_COOKIES` | `True` | Cookies de session et CSRF marqués `Secure`. |
| `DJANGO_SECURE_HSTS_SECONDS` | `0` | Durée HSTS. À activer progressivement une fois HTTPS validé. |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `False` | HSTS sur les sous-domaines. |
| `DJANGO_SECURE_HSTS_PRELOAD` | `False` | Inscription à la liste de préchargement HSTS. |

!!! warning "Exécution locale de l'image de production"
    Sans proxy HTTPS devant l'application, positionnez `DJANGO_SECURE_SSL_REDIRECT=False` et `DJANGO_SECURE_COOKIES=False` (c'est le cas dans `.env.example`).

## Variables PostgreSQL

| Variable | Défaut | Description |
| --- | --- | --- |
| `POSTGRES_DB` | `school_manager` | Nom de la base. |
| `POSTGRES_USER` | `school_manager` | Utilisateur. |
| `POSTGRES_PASSWORD` | vide | Mot de passe (**obligatoire** pour Docker Compose). |
| `POSTGRES_HOST` | `localhost` | Hôte (`db` dans Docker Compose, forcé par le fichier compose). |
| `POSTGRES_PORT` | `5432` | Port. |
| `POSTGRES_CONN_MAX_AGE` | `60` | Durée de vie des connexions persistantes (secondes). |
| `POSTGRES_CONNECT_TIMEOUT` | `5` | Délai maximal de connexion (secondes). |

## Variables applicatives

| Variable | Défaut | Description |
| --- | --- | --- |
| `SCHOOL_DOCUMENT_MAX_SIZE_MB` | `5` | Taille maximale d'un document uploadé. |
| `API_PAGE_SIZE` | `20` | Taille de page de l'API. |
| `API_AUTH_THROTTLE_RATE` | `20/minute` | Limite de requêtes sur l'inscription et la connexion API. |

## Variables d'exploitation

| Variable | Défaut | Description |
| --- | --- | --- |
| `WEB_PORT` | `8000` | Port exposé sur l'hôte par Docker Compose. |
| `PORT` | `8000` | Port d'écoute de Gunicorn dans le conteneur. |
| `GUNICORN_WORKERS` | `3` | Nombre de processus Gunicorn. |
| `GUNICORN_THREADS` | `2` | Threads par processus. |
| `GUNICORN_TIMEOUT` | `30` | Délai maximal d'une requête. |
| `GUNICORN_FORWARDED_ALLOW_IPS` | `127.0.0.1` | IP du proxy autorisées à transmettre `X-Forwarded-*`. |
| `DB_WAIT_TIMEOUT` | `60` | Attente maximale de la base au démarrage du conteneur. |
| `DJANGO_RUN_MIGRATIONS` | `1` | Applique les migrations au démarrage (`0` pour désactiver). |
