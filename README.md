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
## Tempo stimato: 4-5 ore
