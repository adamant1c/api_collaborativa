# `Task Manager Collaborativo` 

## Obiettivo

Realizzare una API per gestire progetti e task collaborativi, con sistema di permessi a livelli tra utenti.

## 💡 Requisiti Funzionali

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

# ⚙️ Installazione

> [!NOTE]
> L'installazione dovrebbe essere effettuata utilizzando python versione 3.10.13
> Verifica la versione di python installata con il comando python --version
> Il progetto è stato sviluppato con o.s. Windows 11 ed è stato testato con o.s. Ubuntu 25.04 plucky

## 1. Clone del progetto

```bash
# Clone da Github

git clone https://github.com/adamant1c/api_collaborativa.git

```

## 2. Creazione Python Virtual Environment e sua attivazione

```bash
# Python Virtual Environment Creation
cd api_collaborativa

python -m venv .venv

source ./.venv/bin/activate
```

## 3. Installazione Requisiti

```bash

pip3 install -r requirements.txt
```

## 4. Creazione file .env

```bash

vim .env
```
Dove il contenuto del file dovrebbe essere:

```
SECRET_KEY='INSERT DJANGO SECRET KEY'
DEBUG=false

DB_NAME=api_database
DB_USER=mooney_user
DB_PASSWORD= INSERT DATABASE PASSWORD   
DB_HOST= INSERT DATABASE IP
DB_PORT= INSERT DATABASE TCP PORT
```


## 5. Avvio Docker Container PostgreSQL

```bash


```


## 5. Migrazioni Database

```bash
cd api_collaborativa
python manage.py makemigrations
python manage.py migrate

```

## 6. Campagna di Test 

### Test Connessione API con Browser

#### API Swagger Documentation:

    http://127.0.0.1:8000/

#### Endpoints:

    http://127.0.0.1:8000/api

### Run Tests Funzionali:  permessi e CRUD

#### Tests Positivi
```bash
pytest -m positivo
```
#### Tests Negativi
```bash
pytest -m negativo
```
#### Tests Progetti
```bash
pytest  -v -s tests/test_projects.py::TestProgettoViewSet
```

#### Tests Tasks
```bash
pytest  -v -s tests/test_projects.py::TestTaskViewSet
```
