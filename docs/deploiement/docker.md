# Dockerisation

## Image applicative — `Dockerfile`

L'image est construite en **deux étapes** :

1. **`builder`** : création d'un environnement virtuel `/opt/venv` et installation de `requirements.txt` ;
2. **`runtime`** : image `python:3.13-slim` minimale qui ne reçoit que l'environnement virtuel et le code.

Bonnes pratiques appliquées :

| Pratique | Mise en œuvre |
| --- | --- |
| Utilisateur non-root | `app` (UID 1001) ; le code appartient à root et est en lecture seule pour l'application |
| Surface d'écriture minimale | Seul `/app/media` (volume) est inscriptible |
| Cache de couches | `requirements.txt` copié et installé avant le code |
| Fichiers statiques | `collectstatic` exécuté au build, servis compressés et versionnés par WhiteNoise |
| Contexte de build réduit | `.dockerignore` exclut secrets (`.env`), caches, médias, rapports |
| Serveur de production | Gunicorn (`docker/gunicorn.conf.py`), workers recyclés (`max_requests`) |
| Supervision | `HEALTHCHECK` sur `/api/health/` |
| Arrêt propre | `exec` dans l'entrypoint : Gunicorn reçoit directement les signaux |

Au démarrage, `docker/entrypoint.sh` :

1. attend la base (`manage.py wait_for_db`) ;
2. applique les migrations (sauf `DJANGO_RUN_MIGRATIONS=0`) ;
3. lance la commande (Gunicorn par défaut).

## Orchestration — `docker-compose.yml`

| Service | Image | Rôle |
| --- | --- | --- |
| `db` | `postgres:16-alpine` | Base de données, volume `postgres_data`, healthcheck `pg_isready` |
| `web` | construite depuis le `Dockerfile` | Application Django, démarre **après** que `db` est sain, volume `media_data` |
| `docs` | `squidfunk/mkdocs-material` | Serveur de documentation (profil optionnel `docs`) |

Les deux services principaux tournent dans des **conteneurs séparés** reliés par le réseau privé `backend` ; seul le port de `web` est publié sur l'hôte.

## Commandes

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
docker compose logs -f web
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py showmigrations
docker compose --profile docs up docs
docker compose down
docker compose down -v
```

`down -v` supprime également les volumes (base et fichiers) : à réserver à une remise à zéro.

## Vérifier le déploiement

```bash
docker compose ps
curl -s http://localhost:8000/api/health/
curl -s -X POST http://localhost:8000/api/auth/register/ -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"Str0ng-Passphrase!","password_confirm":"Str0ng-Passphrase!"}'
```

Résultats attendus : services `db` et `web` à l'état `healthy`, sonde `{"status": "ok", "database": "ok"}`, inscription en `201` avec un jeton.

Ce scénario a été validé de bout en bout sur la pile de production (Gunicorn, paramètres `production`, PostgreSQL 16) : sonde de santé, inscription avec tentative d'auto-attribution du rôle admin (ignorée), refus `403` d'une création par un utilisateur, création/modification par un administrateur, upload puis téléchargement en pièce jointe, révocation du jeton à la déconnexion (`204` puis `401`), suppression d'une école avec nettoyage des fichiers, service des fichiers statiques versionnés, Swagger et administration.

## Lancer les tests dans Docker

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test \
  -e DJANGO_RUN_MIGRATIONS=0 web python manage.py test
```

L'image de production n'embarque pas les outils de développement ; les tests ne nécessitent que les dépendances de `requirements.txt`.
