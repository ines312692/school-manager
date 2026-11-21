# Installation

Deux modes d'installation sont proposés : **Docker** (recommandé, aucune dépendance locale hormis Docker) ou **environnement Python local**.

## Prérequis

| Outil | Version minimale | Usage |
| --- | --- | --- |
| Docker Engine + Compose v2 | 24 / 2.20 | Mode Docker |
| Python | 3.12 (3.13 recommandé) | Mode local |
| PostgreSQL | 14 (16 recommandé) | Mode local |
| GNU Make | optionnel | Raccourcis du `Makefile` |

## Option A — Docker (recommandé)

```bash
git clone <url-du-depot> school-manager
cd school-manager
cp .env.example .env
```

Éditez `.env` et définissez au minimum `DJANGO_SECRET_KEY` et `POSTGRES_PASSWORD`. Pour générer une clé :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Puis :

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Au démarrage, le conteneur `web` attend que PostgreSQL soit prêt (`wait_for_db`), applique les migrations puis lance Gunicorn. Voir [Docker](deploiement/docker.md).

## Option B — Environnement local

### 1. Environnement virtuel et dépendances

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

`requirements-dev.txt` inclut `requirements.txt` ainsi que les outils de développement (tests, lint, documentation).

### 2. Base PostgreSQL

```sql
CREATE ROLE school_manager LOGIN CREATEDB PASSWORD 'school_manager';
CREATE DATABASE school_manager OWNER school_manager;
```

Le droit `CREATEDB` permet à la suite de tests de créer sa base temporaire `test_school_manager`.

Vous pouvez aussi ne démarrer que le service base de données de Docker :

```bash
docker compose up -d db
```

### 3. Variables d'environnement

```bash
cp .env.example .env
```

Pour le développement local, ajustez : `DJANGO_DEBUG=True`, `POSTGRES_HOST=localhost`. Le fichier `.env` est chargé automatiquement (sans écraser les variables déjà définies dans le shell).

### 4. Migrations, super-utilisateur et serveur

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Le super-utilisateur reçoit automatiquement le rôle `admin`.

## Raccourcis `make`

| Commande | Effet |
| --- | --- |
| `make install` | Installe les dépendances de développement |
| `make migrate` | Applique les migrations |
| `make run` | Lance le serveur de développement |
| `make test` | Exécute les tests |
| `make coverage` | Tests + rapport de couverture |
| `make lint` / `make format` | Analyse statique / formatage Ruff |
| `make docs` / `make docs-build` | Sert / génère la documentation |
| `make up` / `make down` / `make logs` | Pilote la pile Docker |
| `make docker-test` | Exécute les tests dans le conteneur |

## Accès

| URL | Description |
| --- | --- |
| `/` | Redirige vers la liste des écoles |
| `/accounts/login/`, `/accounts/signup/` | Connexion et inscription |
| `/schools/` | Liste des écoles |
| `/admin/` | Administration Django |
| `/api/docs/` | Swagger UI |
| `/api/schema/` | Schéma OpenAPI 3 |
| `/api/health/` | Sonde de santé |
