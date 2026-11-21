# Authentification et rôles

## Modèle utilisateur

L'application utilise un **modèle utilisateur personnalisé** (`apps.accounts.models.User`, déclaré via `AUTH_USER_MODEL`) qui hérite de `AbstractUser` et ajoute :

- `email` : obligatoire, normalisé en minuscules, **unique sans tenir compte de la casse** (contrainte PostgreSQL `accounts_user_email_ci_unique`) ;
- `role` : `admin` ou `user` (défaut `user`).

La propriété `is_admin` vaut `True` pour un compte **actif** dont le rôle est `admin` ou qui est super-utilisateur.

## Rôles et droits

| Action | Anonyme | `user` | `admin` |
| --- | :---: | :---: | :---: |
| S'inscrire, se connecter | ✅ | — | — |
| Consulter la liste et le détail des écoles | ❌ | ✅ | ✅ |
| Télécharger un document | ❌ | ✅ | ✅ |
| Créer, modifier, supprimer une école | ❌ | ❌ (403) | ✅ |
| Ajouter, supprimer un document | ❌ | ❌ (403) | ✅ |
| Accéder à `/admin/` | ❌ | ❌ | si `is_staff` |

Règles importantes :

- l'inscription (web ou API) crée **toujours** un compte `user` ; un champ `role` envoyé par le client est ignoré ;
- `createsuperuser` attribue automatiquement le rôle `admin` ;
- la promotion d'un utilisateur se fait dans l'administration Django (`/admin/accounts/user/`), champ « Rôle applicatif ».

## Sécurisation des mots de passe

- **Hachage Argon2id** (`Argon2PasswordHasher`, lauréat de la Password Hashing Competition) en premier dans `PASSWORD_HASHERS`. Les algorithmes PBKDF2 et scrypt restent déclarés pour vérifier d'anciens hachages, qui sont automatiquement réencodés en Argon2 à la connexion suivante.
- **Validateurs** : longueur minimale de 10 caractères, refus des mots de passe courants, entièrement numériques ou trop proches des attributs de l'utilisateur.
- Les mots de passe ne sont jamais renvoyés par l'API (`write_only`) et ne sont jamais journalisés.
- Les points d'entrée `register` et `login` de l'API sont **limités en débit** (`API_AUTH_THROTTLE_RATE`, 20 requêtes/minute par défaut) contre la force brute.
- En cas d'échec de connexion, le message est volontairement générique (« Identifiants invalides. »).

## Pages web

| URL | Méthode | Description |
| --- | --- | --- |
| `/accounts/signup/` | GET, POST | Formulaire d'inscription ; connecte l'utilisateur après création. |
| `/accounts/login/` | GET, POST | Connexion par session. |
| `/accounts/logout/` | POST | Déconnexion (POST uniquement, protégé par CSRF). |

## API d'authentification

L'API utilise l'**authentification par jeton** de DRF (`Authorization: Token <clé>`). L'authentification par session reste acceptée pour l'API navigable et Swagger.

### Inscription — `POST /api/auth/register/`

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "lea", "email": "lea@example.com", "first_name": "Léa", "last_name": "Martin",
       "password": "Str0ng-Passphrase!", "password_confirm": "Str0ng-Passphrase!"}'
```

Réponse `201 Created` :

```json
{
  "token": "10986c1456587a17a843aa99ad5714e8fc8be7c7",
  "user": {
    "id": 2, "username": "lea", "email": "lea@example.com",
    "first_name": "Léa", "last_name": "Martin", "role": "user",
    "date_joined": "2026-11-19T16:00:48.266566+01:00"
  }
}
```

Erreurs `400` : e-mail déjà utilisé, mots de passe différents (`password_confirm`), mot de passe trop faible (`password`), champ manquant.

### Connexion — `POST /api/auth/login/`

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "lea", "password": "Str0ng-Passphrase!"}'
```

Réponse `200 OK` au même format que l'inscription. Met à jour `last_login`. Un compte désactivé ne peut pas se connecter (`400`).

### Profil — `GET /api/auth/me/`

```bash
curl http://localhost:8000/api/auth/me/ -H "Authorization: Token <clé>"
```

### Déconnexion — `POST /api/auth/logout/`

```bash
curl -X POST http://localhost:8000/api/auth/logout/ -H "Authorization: Token <clé>"
```

Réponse `204 No Content`. Le jeton est **révoqué** (supprimé en base) : toute requête ultérieure avec ce jeton reçoit `401`. Si la requête est authentifiée par session, la session est également fermée.

!!! info "Un jeton par utilisateur"
    Le modèle `Token` de DRF associe un jeton unique à chaque utilisateur. Une déconnexion révoque donc l'accès sur tous les clients API de cet utilisateur. Pour des jetons multiples à durée de vie limitée, voir les pistes d'évolution dans [Mise en production](../deploiement/production.md).
