# Task Manager Collaborativo

## Obiettivo

Realizzare una API per gestire progetti e task collaborativi, con sistema di permessi a livelli tra utenti.

## Requisiti Funzionali

```
Autenticazione JWT
CRUD per:
Progetto
Task (collegato a un progetto)
Ogni progetto ha un ** proprietario ** e può avere ** collaboratori **
Solo il proprietario può:
aggiungere/rimuovere collaboratori
cancellare il progetto
I collaboratori possono solo:
creare/modificare task nel progetto
```
## Extra:

```
Scadenza task e stato (`TODO`, `IN PROGRESS`, `DONE`)
Statistiche sui task (es: percentuale completati per progetto)
```
## Strumenti richiesti:

```
Django, DRF, PostgreSQL, SimpleJWT
Test base (almeno su permessi e CRUD)
```

# Lista  degli endpoints disponibili:
```
Authentication:
POST /api/auth/register/          - Registrazione
POST /api/auth/logout/            - Logout
GET  /api/auth/profile/           - Profilo utente
POST /api/auth/token/             - Richiesta token da credenziali
POST /api/auth/token/refresh      - Refresh del token scaduto

Projects:
GET    /api/projects/             - Lista progetti
POST   /api/projects/             - Crea progetto
GET    /api/projects/{id}/        - Dettaglio progetto
PUT    /api/projects/{id}/        - Aggiorna progetto
PATCH    /api/projects/{id}/        - Aggiornamento parziale progetto
DELETE /api/projects/{id}/        - Elimina progetto
POST   /api/projects/{id}/add_collaborator/     - Aggiungi collaboratore
POST   /api/projects/{id}/remove_collaborator/  - Rimuovi collaboratore
GET    /api/projects/{id}/stats/  - Statistiche progetto
GET    /api/projects/{id}/tasks/  - Task del progetto

Tasks:
GET    /api/tasks/               - Lista task
POST   /api/tasks/               - Crea task
GET    /api/tasks/{id}/          - Dettaglio task
PUT    /api/tasks/{id}/          - Aggiorna task
PATCH    /api/tasks/{id}/        - Aggiornamento parziale task
DELETE /api/tasks/{id}/          - Elimina task
```