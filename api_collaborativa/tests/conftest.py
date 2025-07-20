import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from progetti.models import Progetto
from progetti.models import Task

#Nota: db =	Fixture di pytest-django per abilitare accesso al DB Django

@pytest.fixture(scope='function')
def user_proprietario(db):
    """User è un utente puro per Creare/modificare dati nel DB"""
    return User.objects.create_user(username='owner', password='testpass')





@pytest.fixture(scope='function')
def user_collaboratore(db):
    """User è un utente puro per Creare/modificare dati nel DB"""
    return User.objects.create_user(username='collab', password='testpass')


@pytest.fixture(scope='function')
def user_estraneo(db):
    """User è un utente puro per Creare/modificare dati nel DB"""
    return User.objects.create_user(username='estraneo', password='testpass')


@pytest.fixture
def client_autenticato(user_proprietario):
    client = APIClient()
    refresh = RefreshToken.for_user(user_proprietario)
    access_token = str(refresh.access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return client


@pytest.fixture(scope='function')
def client_collaboratore(user_collaboratore):
    """Client autenticato come collaboratore (JWT)"""
    client = APIClient()
    refresh = RefreshToken.for_user(user_collaboratore)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return client

@pytest.fixture(scope='function')
def client_estraneo(user_estraneo):
    """Client autenticato come utente estraneo (JWT)"""
    client = APIClient()
    refresh = RefreshToken.for_user(user_estraneo)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return client

@pytest.fixture(scope='function')
def progetto(user_proprietario, user_collaboratore):
    progetto = Progetto.objects.create(
        nome="Progetto Test",
        descrizione="Un progetto di test",
        proprietario=user_proprietario
    )
    progetto.collaboratori.add(user_collaboratore)
    return progetto


@pytest.fixture
def task(user_proprietario, progetto):
    return Task.objects.create(
        titolo='Task iniziale',
        descrizione='Descrizione',
        progetto=progetto,
        autore=user_proprietario,
        stato='TODO'
    )



@pytest.fixture
def task_creato_dal_collaboratore(progetto, user_collaboratore):
    return Task.objects.create(
        titolo='Task Collab',
        progetto=progetto,
        autore=user_collaboratore,
        stato='TODO'
    )

@pytest.fixture
def api_client():
    return APIClient()