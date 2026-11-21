# Gestion des écoles

## Modèle `School`

| Champ | Type | Règles |
| --- | --- | --- |
| `name` | texte (255) | obligatoire |
| `address` | texte (255) | obligatoire |
| `city` | texte (120) | obligatoire, indexé |
| `postal_code` | texte (10) | obligatoire, 3 à 10 caractères alphanumériques |
| `student_count` | entier positif | 0 à 100 000, défaut 0 |
| `email` | e-mail | optionnel |
| `phone` | texte (20) | optionnel, format téléphonique |
| `website` | URL | optionnel |
| `created_by` | utilisateur | renseigné automatiquement, conservé à `NULL` si l'auteur est supprimé |
| `created_at`, `updated_at` | horodatages | automatiques |

**Unicité** : le couple (nom, ville) est unique **sans tenir compte de la casse**. « Lycée Victor Hugo » à Paris et « lycée victor hugo » à PARIS sont considérés comme la même école ; le même nom reste possible dans une autre ville. La règle est garantie par la contrainte PostgreSQL `schools_school_name_city_ci_unique` et vérifiée en amont par le formulaire et le sérialiseur (erreur `400` explicite).

## Pages web

Toutes les pages exigent d'être connecté ; les pages d'écriture exigent le rôle `admin` (sinon `403`).

| URL | Rôle | Description |
| --- | --- | --- |
| `/schools/` | tous | Liste paginée (10 par page), recherche par nom, ville ou code postal, nombre de documents. |
| `/schools/<id>/` | tous | Fiche détaillée et documents ; formulaire d'upload pour les administrateurs. |
| `/schools/new/` | admin | Création. |
| `/schools/<id>/edit/` | admin | Modification. |
| `/schools/<id>/delete/` | admin | Confirmation puis suppression (documents et fichiers inclus). |

Chaque opération réussie affiche un message de confirmation. Les liens d'action ne sont affichés qu'aux administrateurs.

## API REST

Base : `/api/schools/` — authentification requise.

| Méthode | URL | Rôle | Description |
| --- | --- | --- | --- |
| GET | `/api/schools/` | tous | Liste paginée |
| POST | `/api/schools/` | admin | Création (`201`) |
| GET | `/api/schools/{id}/` | tous | Détail |
| PUT | `/api/schools/{id}/` | admin | Remplacement complet |
| PATCH | `/api/schools/{id}/` | admin | Mise à jour partielle |
| DELETE | `/api/schools/{id}/` | admin | Suppression (`204`) |

### Recherche, tri et pagination

| Paramètre | Exemple | Effet |
| --- | --- | --- |
| `search` | `?search=lyon` | Recherche dans le nom, la ville et le code postal |
| `ordering` | `?ordering=-student_count` | Tri sur `name`, `city`, `student_count`, `created_at` (préfixe `-` = décroissant) |
| `page` | `?page=2` | Page demandée (taille : `API_PAGE_SIZE`) |

### Exemples

Création :

```bash
curl -X POST http://localhost:8000/api/schools/ \
  -H "Authorization: Token <clé-admin>" -H "Content-Type: application/json" \
  -d '{"name": "Lycée Henri IV", "address": "23 rue Clovis", "city": "Paris",
       "postal_code": "75005", "student_count": 2500}'
```

```json
{
  "id": 1, "name": "Lycée Henri IV", "address": "23 rue Clovis", "city": "Paris",
  "postal_code": "75005", "student_count": 2500, "email": "", "phone": "", "website": "",
  "document_count": 0, "created_by": "admin",
  "created_at": "2026-11-19T16:00:48.690404+01:00", "updated_at": "2026-11-19T16:00:48.690421+01:00"
}
```

Mise à jour partielle :

```bash
curl -X PATCH http://localhost:8000/api/schools/1/ \
  -H "Authorization: Token <clé-admin>" -H "Content-Type: application/json" \
  -d '{"student_count": 2600}'
```

Suppression :

```bash
curl -X DELETE http://localhost:8000/api/schools/1/ -H "Authorization: Token <clé-admin>"
```

## Administration Django

`/admin/schools/school/` propose recherche, filtre par ville et édition des documents en ligne. L'auteur de l'école et l'auteur de chaque document y sont renseignés automatiquement.
