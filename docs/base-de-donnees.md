# Base de données PostgreSQL

## Configuration

Le moteur est `django.db.backends.postgresql` avec le pilote **psycopg 3**. Les paramètres proviennent des variables `POSTGRES_*` (voir [Configuration](configuration.md)). Sont activés :

- les **connexions persistantes** (`CONN_MAX_AGE=60`) pour éviter le coût d'une connexion par requête ;
- les **vérifications de santé des connexions** (`CONN_HEALTH_CHECKS=True`) : une connexion persistante coupée est détectée et rouverte de façon transparente ;
- un **délai de connexion** borné (`connect_timeout=5`).

## Tables

| Table | Contenu |
| --- | --- |
| `accounts_user` | Utilisateurs, rôle, mot de passe haché |
| `authtoken_token` | Jetons d'API |
| `schools_school` | Écoles |
| `schools_schooldocument` | Métadonnées des documents (le contenu est sur disque, volume `media_data`) |
| `django_session`, `auth_*`, `django_*` | Tables du framework |

Contraintes et index notables :

| Nom | Type | Rôle |
| --- | --- | --- |
| `accounts_user_email_ci_unique` | `UNIQUE (LOWER(email))` | Une adresse par compte, casse ignorée |
| `schools_school_name_city_ci_unique` | `UNIQUE (LOWER(name), LOWER(city))` | Pas de doublon d'école dans une ville |
| `schools_city_idx` | index B-tree | Filtrage par ville |
| `student_count` | `CHECK (>= 0)` | Garanti par `PositiveIntegerField` |

## Migrations

Les migrations sont versionnées dans `apps/accounts/migrations/` et `apps/schools/migrations/`.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate schools 0001
```

En Docker, `migrate` est exécuté automatiquement au démarrage du conteneur `web` (désactivable avec `DJANGO_RUN_MIGRATIONS=0`, utile lorsque plusieurs répliques démarrent en parallèle et que les migrations sont jouées par une tâche dédiée).

## Vérifier la connexion et les migrations

| Vérification | Commande | Résultat attendu |
| --- | --- | --- |
| Joignabilité de la base | `python manage.py wait_for_db --timeout 30` | `Base de données « default » disponible.` |
| Sonde HTTP | `curl http://localhost:8000/api/health/` | `{"status": "ok", "database": "ok"}` (sinon `503`) |
| Migrations appliquées | `python manage.py showmigrations` | Toutes les lignes cochées `[X]` |
| Pas de migration manquante | `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| Contrôles Django | `python manage.py check --deploy --settings=config.settings.production` | Aucune erreur |

Ces vérifications sont également **automatisées dans la suite de tests** (`apps/core/tests/test_health.py`) : moteur PostgreSQL effectivement utilisé, plan de migration vide après `migrate`, absence de migration manquante, comportement de `wait_for_db` et de `/api/health/` en cas de panne.

## Sauvegarde et restauration (Docker)

```bash
docker compose exec -T db pg_dump -U school_manager -d school_manager -Fc > backup.dump
docker compose exec -T db pg_restore -U school_manager -d school_manager --clean < backup.dump
```

Pensez à sauvegarder aussi le volume `media_data`, qui contient les fichiers uploadés.
