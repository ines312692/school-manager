# Tests

La suite utilise le framework de test intégré à Django (`django.test.TestCase`) et `rest_framework.test.APITestCase`. Elle s'exécute sur **PostgreSQL**, le même moteur qu'en production, afin de valider réellement les contraintes fonctionnelles (`LOWER(...)`).

## Lancer les tests

=== "Local"

    ```bash
    python manage.py test --settings=config.settings.test
    ```

=== "Avec couverture"

    ```bash
    coverage run manage.py test --settings=config.settings.test
    coverage report
    ```

=== "Docker"

    ```bash
    docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test \
      -e DJANGO_RUN_MIGRATIONS=0 web python manage.py test
    ```

=== "Make"

    ```bash
    make test
    make coverage
    make docker-test
    ```

Le module `config.settings.test` accélère l'exécution (hachage MD5 réservé aux tests, cache factice qui désactive la limitation de débit) et chaque classe manipulant des fichiers utilise un `MEDIA_ROOT` temporaire supprimé en fin de test (`TemporaryMediaRootMixin`).

## Périmètre couvert

| Module | Tests | Ce qui est vérifié |
| --- | ---: | --- |
| `accounts.tests.test_models` | 8 | Rôle par défaut, super-utilisateur ⇒ admin, compte inactif sans droits, mot de passe haché (Argon2), e-mail normalisé et unique sans casse |
| `accounts.tests.test_api` | 14 | Inscription (jeton, hachage, rôle forcé à `user`, doublon, mots de passe différents ou faibles), connexion (succès, `last_login`, mauvais mot de passe, compte inactif), déconnexion (révocation du jeton, `401`), `/me` |
| `accounts.tests.test_views` | 7 | Pages d'inscription, de connexion et de déconnexion |
| `schools.tests.test_models` | 6 | Représentation, URL, unicité nom/ville en base et en validation, validateurs |
| `schools.tests.test_api` | 17 | CRUD complet par un admin, refus `403` pour un `user`, `401` anonyme, recherche, tri, validation, doublons |
| `schools.tests.test_views` | 13 | Pages liste/détail/création/modification/suppression, contrôle des rôles, recherche |
| `schools.tests.test_documents` | 24 | Upload (API et page), métadonnées, nom aléatoire, extension et taille refusées, téléchargement en pièce jointe, `404` si fichier absent, suppression et remplacement avec nettoyage du disque, droits |
| `schools.tests.test_admin` | 4 | Administration : auteur renseigné, documents en ligne |
| `core.tests.test_health` | 7 | Moteur PostgreSQL, migrations appliquées et à jour, `wait_for_db`, `/api/health/` (200 et 503) |
| `core.tests.test_env` | 6 | Lecture et validation des variables d'environnement |
| `core.tests.test_api_schema` | 1 | Génération du schéma OpenAPI |
| **Total** | **107** | |

## Résultats

Dernière exécution (PostgreSQL 16, Python 3.13, Django 5.2) :

```text
Ran 107 tests in 1.463s

OK
```

Couverture de code : **98 %** (seuil minimal configuré : 90 %).

Les rapports complets sont livrés dans le dépôt :

- `reports/test-results.txt` : sortie détaillée (`-v 2`) de chaque test ;
- `reports/coverage.txt` : couverture ligne par ligne et par branche.

## Qualité du code

```bash
ruff check .
ruff format --check .
```

Les règles Ruff activées incluent pycodestyle, Pyflakes, isort, bugbear, pyupgrade, les règles Django (`DJ`) et les règles de sécurité Bandit (`S`). L'intégration continue (`.github/workflows/ci.yml`) exécute lint, contrôles Django, vérification des migrations, tests avec couverture et construction de la documentation sur chaque push.
