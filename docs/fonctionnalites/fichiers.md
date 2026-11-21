# Upload de fichiers

Chaque école peut recevoir des **documents** (projet d'établissement, règlement, bilans…), modélisés par `SchoolDocument`.

## Règles de validation

| Règle | Valeur par défaut | Paramètre |
| --- | --- | --- |
| Extensions autorisées | `pdf, png, jpg, jpeg, doc, docx, xls, xlsx, csv, txt` | `SCHOOL_DOCUMENT_ALLOWED_EXTENSIONS` (settings) |
| Taille maximale | 5 Mo | `SCHOOL_DOCUMENT_MAX_SIZE_MB` (environnement) |

Les validateurs (`apps/schools/validators.py`) sont attachés au champ du modèle : ils s'appliquent identiquement aux formulaires web, à l'API et à l'administration. Ils lisent les paramètres à l'exécution, ce qui permet de les ajuster sans migration.

## Stockage et sécurité

- **Nom de fichier non devinable** : le fichier est stocké sous `schools/<id_école>/documents/<uuid4>.<ext>`. Le nom d'origine est conservé en base (`original_name`) mais jamais utilisé comme chemin, ce qui neutralise les attaques par traversée de répertoire et les collisions.
- **Métadonnées capturées automatiquement** : nom d'origine, type MIME, taille ; le titre prend par défaut le nom du fichier sans extension.
- **Aucune exposition publique de `MEDIA_ROOT`** : les fichiers ne sont servis que par une vue authentifiée, en pièce jointe (`Content-Disposition: attachment`), ce qui empêche l'interprétation d'un fichier malveillant dans le navigateur.
- **Nettoyage du disque** : à la suppression d'un document (ou de son école, en cascade) et au remplacement d'un fichier, l'ancien fichier est supprimé du stockage **après validation de la transaction** (`transaction.on_commit`) : un rollback ne provoque jamais de perte de fichier.
- **Permissions** : fichiers créés en `0640`, répertoires en `0750` ; dans Docker, le volume `media_data` est le seul répertoire inscriptible par l'utilisateur non-root de l'application.

## Pages web

| URL | Rôle | Description |
| --- | --- | --- |
| `/schools/<id>/` | admin | Formulaire d'upload intégré à la fiche école |
| `/schools/<id>/documents/new/` | admin | Réception de l'upload (formulaire réaffiché en cas d'erreur) |
| `/schools/documents/<id>/download/` | tous | Téléchargement |
| `/schools/documents/<id>/delete/` | admin | Suppression |

## API REST

| Méthode | URL | Rôle | Description |
| --- | --- | --- | --- |
| GET | `/api/schools/{id}/documents/` | tous | Documents d'une école (paginé) |
| POST | `/api/schools/{id}/documents/` | admin | Upload (`multipart/form-data`) |
| GET | `/api/documents/` | tous | Tous les documents ; filtre `?school=<id>`, `search`, `ordering` |
| GET | `/api/documents/{id}/` | tous | Métadonnées |
| GET | `/api/documents/{id}/download/` | tous | Contenu du fichier |
| DELETE | `/api/documents/{id}/` | admin | Suppression (fichier inclus) |

Upload :

```bash
curl -X POST http://localhost:8000/api/schools/1/documents/ \
  -H "Authorization: Token <clé-admin>" \
  -F "title=Projet d'établissement" \
  -F "file=@projet.pdf"
```

```json
{
  "id": 1, "school": 1, "title": "Projet d'établissement",
  "original_name": "projet.pdf", "content_type": "application/pdf", "size": 48213,
  "uploaded_by": "admin", "uploaded_at": "2026-11-19T16:00:48.732834+01:00",
  "download_url": "http://localhost:8000/api/documents/1/download/"
}
```

Téléchargement :

```bash
curl -OJ http://localhost:8000/api/documents/1/download/ -H "Authorization: Token <clé>"
```

Erreurs : `400` (fichier absent, extension refusée, taille dépassée), `403` (rôle insuffisant), `404` (document ou fichier introuvable).
