# Architecture

## Arborescence

```text
school-manager/
├── apps/
│   ├── core/                 Socle transverse
│   │   ├── database.py         Vérification de la connexion à la base
│   │   ├── models.py           TimeStampedModel (created_at / updated_at)
│   │   ├── testing.py          Fabriques et utilitaires de test
│   │   ├── views.py            Sonde /api/health/
│   │   └── management/commands/wait_for_db.py
│   ├── accounts/             Utilisateurs, rôles, authentification
│   │   ├── models.py           User (AbstractUser + rôle)
│   │   ├── managers.py         create_superuser ⇒ rôle admin
│   │   ├── services.py         Jetons, unicité de l'e-mail
│   │   ├── permissions.py      Permissions DRF par rôle
│   │   ├── mixins.py           Mixin de vue « admin requis »
│   │   ├── forms.py / views.py / urls.py   Pages web
│   │   └── api/                Sérialiseurs, vues et routes API
│   └── schools/              Écoles et documents
│       ├── models.py           School, SchoolDocument
│       ├── validators.py       Extension et taille des fichiers
│       ├── signals.py          Nettoyage des fichiers sur disque
│       ├── services.py         Recherche, unicité, réponse de téléchargement
│       ├── forms.py / views.py / urls.py   Pages web
│       └── api/                Sérialiseurs, ViewSets, routeur
├── config/
│   ├── env.py                Lecture typée des variables d'environnement
│   ├── settings/             base, development, test, production
│   ├── urls.py / api_urls.py
│   └── wsgi.py / asgi.py
├── templates/ · static/      Interface web
├── docker/                   entrypoint.sh, gunicorn.conf.py
├── docs/ · mkdocs.yml        Documentation (source)
├── site/                     Documentation générée
├── reports/                  Résultats de tests et couverture
├── Dockerfile · docker-compose.yml
├── requirements.txt · requirements-dev.txt
└── Makefile · pyproject.toml
```

## Principes de conception

**Applications par domaine.** Chaque application Django porte un domaine métier (`accounts`, `schools`) ; `core` regroupe le transverse. Les dépendances vont toujours de `schools` vers `accounts`, jamais l'inverse.

**Couche de services.** La logique réutilisée par plusieurs points d'entrée (pages web, API, administration) vit dans `services.py` : émission/révocation des jetons, contrôle d'unicité, construction de la réponse de téléchargement. Les vues restent fines.

**Règles d'intégrité au plus près des données.** Les unicités insensibles à la casse sont garanties par des contraintes PostgreSQL fonctionnelles (`UniqueConstraint(Lower(...))`) et vérifiées en amont par les formulaires et sérialiseurs pour renvoyer une erreur 400 lisible plutôt qu'une erreur d'intégrité.

**Autorisation centralisée.** Une seule source de vérité pour le rôle : la propriété `User.is_admin`. Elle alimente la permission DRF `IsAdminRoleOrReadOnly`, le mixin `AdminRoleRequiredMixin` et les gabarits.

**Configuration externalisée.** Aucun secret dans le code ; `config/env.py` valide les types (booléens, entiers, listes) et échoue explicitement (`ImproperlyConfigured`) sur une valeur invalide.

## Flux d'une requête API

```text
Client ──HTTP──▶ Gunicorn ──▶ Middlewares Django (sécurité, WhiteNoise, sessions, CSRF)
                                   │
                                   ▼
                       Routeur DRF (/api/…)
                                   │
            Authentification : TokenAuthentication puis SessionAuthentication
                                   │
            Permission : IsAuthenticated / IsAdminRoleOrReadOnly
                                   │
            ViewSet ──▶ Sérialiseur (validation) ──▶ Modèle / Service ──▶ PostgreSQL
```

## Modèle de données

```text
accounts_user                     schools_school                     schools_schooldocument
─────────────                     ──────────────                     ──────────────────────
id                  ◀──┐          id                    ◀────────┐   id
username (unique)      ├──────────created_by (FK, null)          ├───school (FK, CASCADE)
email (unique, ci)     │          name  ┐ unique (ci)            │   title
role (admin|user)      │          city  ┘                        │   file (chemin aléatoire)
password (argon2)      │          address, postal_code           │   original_name
is_active, …           │          student_count (0…100 000)      │   content_type, size
                       │          email, phone, website          │   uploaded_at
                       └──────────────────────────────────────── └───uploaded_by (FK, null)
                                  created_at, updated_at
```

`ci` : insensible à la casse.
