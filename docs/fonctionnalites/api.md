# Référence de l'API

## Généralités

| Élément | Valeur |
| --- | --- |
| Préfixe | `/api/` |
| Format | JSON (`multipart/form-data` pour l'upload) |
| Authentification | `Authorization: Token <clé>` (ou session) |
| Pagination | `{"count", "next", "previous", "results"}` |
| Documentation interactive | `/api/docs/` (Swagger UI) |
| Schéma OpenAPI 3 | `/api/schema/` |

## Points d'entrée

| Méthode | URL | Auth | Rôle | Description |
| --- | --- | :---: | :---: | --- |
| GET | `/api/health/` | — | — | Sonde de santé (application + base) |
| POST | `/api/auth/register/` | — | — | Inscription, renvoie un jeton |
| POST | `/api/auth/login/` | — | — | Connexion, renvoie un jeton |
| POST | `/api/auth/logout/` | ✅ | tous | Révocation du jeton |
| GET | `/api/auth/me/` | ✅ | tous | Utilisateur courant |
| GET | `/api/schools/` | ✅ | tous | Liste des écoles |
| POST | `/api/schools/` | ✅ | admin | Création d'une école |
| GET | `/api/schools/{id}/` | ✅ | tous | Détail d'une école |
| PUT / PATCH | `/api/schools/{id}/` | ✅ | admin | Modification |
| DELETE | `/api/schools/{id}/` | ✅ | admin | Suppression |
| GET | `/api/schools/{id}/documents/` | ✅ | tous | Documents d'une école |
| POST | `/api/schools/{id}/documents/` | ✅ | admin | Upload d'un document |
| GET | `/api/documents/` | ✅ | tous | Liste des documents (`?school=`) |
| GET | `/api/documents/{id}/` | ✅ | tous | Métadonnées d'un document |
| GET | `/api/documents/{id}/download/` | ✅ | tous | Téléchargement |
| DELETE | `/api/documents/{id}/` | ✅ | admin | Suppression d'un document |

## Codes de réponse

| Code | Signification |
| --- | --- |
| `200` / `201` / `204` | Succès (lecture / création / suppression ou déconnexion) |
| `400` | Données invalides ; le corps détaille les erreurs par champ |
| `401` | Non authentifié ou jeton invalide/révoqué |
| `403` | Authentifié mais rôle insuffisant |
| `404` | Ressource introuvable |
| `429` | Trop de tentatives d'inscription/connexion |
| `503` | `/api/health/` : base de données indisponible |

Exemple d'erreur de validation :

```json
{
  "student_count": ["Assurez-vous que cette valeur est supérieure ou égale à 0."],
  "email": ["Saisissez une adresse e-mail valide."]
}
```

## Scénario complet

```bash
API=http://localhost:8000/api

TOKEN=$(curl -s -X POST $API/auth/login/ -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "<mot-de-passe>"}' | jq -r .token)

curl -s -X POST $API/schools/ -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "Collège Marie Curie", "address": "12 avenue des Sciences", "city": "Grenoble", "postal_code": "38000", "student_count": 480}'

curl -s -X POST $API/schools/1/documents/ -H "Authorization: Token $TOKEN" -F "file=@reglement.pdf"

curl -s "$API/schools/?search=grenoble&ordering=-student_count" -H "Authorization: Token $TOKEN"

curl -s -X POST $API/auth/logout/ -H "Authorization: Token $TOKEN"
```
