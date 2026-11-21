# Mise en production

## Liste de contrôle

- [ ] `DJANGO_SECRET_KEY` longue, aléatoire et propre à l'environnement ;
- [ ] `DJANGO_DEBUG=False` (forcé par `config.settings.production`) ;
- [ ] `DJANGO_ALLOWED_HOSTS` et `DJANGO_CSRF_TRUSTED_ORIGINS` limités au domaine réel ;
- [ ] Application derrière un proxy inverse HTTPS (Nginx, Traefik, équilibreur cloud) qui transmet `X-Forwarded-Proto` ;
- [ ] `GUNICORN_FORWARDED_ALLOW_IPS` renseigné avec l'adresse du proxy ;
- [ ] `DJANGO_SECURE_SSL_REDIRECT=True`, `DJANGO_SECURE_COOKIES=True` ;
- [ ] HSTS activé progressivement (`DJANGO_SECURE_HSTS_SECONDS=3600`, puis `31536000`) ;
- [ ] Mot de passe PostgreSQL fort, base non exposée publiquement ;
- [ ] Sauvegardes régulières de la base **et** du volume `media_data` ;
- [ ] `python manage.py check --deploy` sans avertissement bloquant.

## En-têtes et protections actives

`config.settings.production` active : redirection HTTPS (sauf la sonde de santé), cookies `Secure` et `HttpOnly`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`, prise en compte de `X-Forwarded-Proto`, et restreint l'API au rendu JSON (l'API navigable n'est pas exposée).

## Montée en charge

- Ajuster `GUNICORN_WORKERS` (≈ 2 × cœurs + 1) et `GUNICORN_THREADS` ;
- Lors d'un déploiement multi-répliques, jouer les migrations une seule fois (tâche dédiée) et démarrer les répliques avec `DJANGO_RUN_MIGRATIONS=0` ;
- Pour un stockage partagé des documents entre répliques, remplacer le stockage `default` de `STORAGES` par un stockage objet (par exemple S3 via `django-storages`) : le code applicatif n'a pas à changer.

## Pistes d'évolution

- Jetons à durée de vie limitée et multiples par utilisateur (`django-rest-knox` ou JWT via `djangorestframework-simplejwt`) ;
- Vérification du type réel des fichiers par signature binaire (`python-magic`) et analyse antivirus (ClamAV) ;
- Journalisation structurée (JSON) et traçage des actions d'administration ;
- Réinitialisation du mot de passe par e-mail.
