# Dépendances

Les versions sont **épinglées** pour garantir des builds reproductibles.

## `requirements.txt` — exécution

| Paquet | Version | Rôle |
| --- | --- | --- |
| Django | 5.2.19 | Framework web (version LTS, supportée jusqu'en avril 2028) |
| djangorestframework | 3.18.3 | API REST, authentification par jeton, permissions, pagination |
| drf-spectacular | 0.30.0 | Schéma OpenAPI 3 et Swagger UI |
| psycopg[binary] | 3.3.9 | Pilote PostgreSQL |
| argon2-cffi | 25.1.0 | Hachage Argon2 des mots de passe |
| python-dotenv | 1.2.3 | Chargement du fichier `.env` |
| whitenoise | 6.12.0 | Service des fichiers statiques compressés et versionnés |
| gunicorn | 27.0.1 | Serveur WSGI de production |

## `requirements-dev.txt` — développement

Inclut `requirements.txt` et ajoute :

| Paquet | Version | Rôle |
| --- | --- | --- |
| coverage | 7.17.3 | Mesure de couverture des tests |
| ruff | 0.17.5 | Lint et formatage |
| mkdocs | 1.6.1 | Générateur de documentation |
| mkdocs-material | 9.7.7 | Thème de la documentation |

## Mettre à jour

```bash
pip install -U -r requirements-dev.txt
python manage.py test --settings=config.settings.test
pip freeze
```

Reportez ensuite les nouvelles versions validées dans les fichiers de dépendances.
