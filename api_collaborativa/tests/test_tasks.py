import pytest
from django.urls import reverse
from rest_framework import status

from progetti.models import Task

@pytest.mark.django_db
class TestTaskViewSet:
    """
    Test di verifica delle operazioni CRUD sui task.
    Ogni test utilizza client autenticati come proprietario, collaboratore o estraneo
    e interagisce con un progetto condiviso (fixture `progetto`) e task associati.
    """
    @pytest.mark.positivo
    def test_proprietario_puo_creare_task(self, client_proprietario, progetto):
        url = reverse('tasks-list')
        response = client_proprietario.post(url, {
            'titolo': 'Task 1',
            'descrizione': 'Descrizione task',
            'progetto': progetto.id,
            'stato': 'TODO'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['titolo'] == 'Task 1'

    @pytest.mark.positivo
    def test_collaboratore_puo_creare_task(self, client_collaboratore, progetto):
        """
          Test: Un collaboratore può creare un task nel progetto.

          Step:
          1. Invio di una richiesta POST con i dati del task.
          2. Verifica che il task sia stato creato con stato HTTP 201.
        """
        url = reverse('tasks-list')
        response = client_collaboratore.post(url, {
            'titolo': 'Task 2',
            'descrizione': 'Creato dal collaboratore',
            'progetto': progetto.id,
            'stato': 'TODO'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.negativo
    def test_estraneo_non_puo_creare_task(self, client_estraneo, progetto):
        """
         Test: Un utente estraneo non può creare un task in un progetto a cui non appartiene.

         Step:
         1. Invio di una richiesta POST.
         2. Verifica che venga negato l'accesso (403 FORBIDDEN).
         """
        url = reverse('tasks-list')
        response = client_estraneo.post(url, {
            'titolo': 'Task vietato',
            'progetto': progetto.id,
            'stato': 'TODO'
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_autore_puo_modificare_task(self, client_proprietario, task):
        """
        Test: L'autore del task può modificarlo.

        Step:
        1. Invio PATCH per modificare il titolo del task.
        2. Verifica dello stato 200 e del campo aggiornato.
        """
        url = reverse('tasks-detail', args=[task.id])
        response = client_proprietario.patch(url, {
            'titolo': 'Nuovo Titolo'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['titolo'] == 'Nuovo Titolo'

    @pytest.mark.positivo
    def test_collaboratore_puo_modificare_task(self, client_collaboratore, task):
        url = reverse('tasks-detail', args=[task.id])
        response = client_collaboratore.patch(url, {
            'stato': 'IN_PROGRESS'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.negativo
    def test_estraneo_non_puo_accedere_task(self, client_estraneo, task):
        url = reverse('tasks-detail', args=[task.id])
        response = client_estraneo.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.negativo
    def test_collaboratore_non_puo_eliminare_task_non_suo(self, client_collaboratore, task):
        """
       Test: Un collaboratore diverso dall'autore non può eliminare un task.

       Step:
       1. Invio DELETE da parte di altro collaboratore.
       2. Verifica che venga restituito 403 FORBIDDEN.
       """
        url = reverse('tasks-detail', args=[task.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_autore_puo_eliminare_task_proprio(self, user_collaboratore, client_collaboratore, progetto):
        """
        Test: L'autore può eliminare il proprio task.

        Step:
        1. Invio DELETE.
        2. Verifica che il task sia stato eliminato.
        """
        task = Task.objects.create(
            titolo='Creato da collab',
            progetto=progetto,
            autore=user_collaboratore
        )
        url = reverse('tasks-detail', args=[task.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.positivo
    def test_proprietario_puo_aggiungere_collaboratore(self, client_proprietario, progetto, user_estraneo):
        """
       Test: Il proprietario può aggiungere un collaboratore al progetto.

       Steps:
       1. Effettua una richiesta POST con l'username dell'utente estraneo.
       2. Verifica che venga aggiunto come collaboratore (201 CREATED).
       """
        url = reverse('projects-add-collaborator', args=[progetto.id])
        response = client_proprietario.post(url, {
            'user_id': user_estraneo.id
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert progetto.collaboratori.filter(id=user_estraneo.id).exists()

    @pytest.mark.positivo
    def test_proprietario_puo_rimuovere_collaboratore(self, client_proprietario, progetto, user_collaboratore):
        url = reverse('projects-remove-collaborator', args=[progetto.id])
        response = client_proprietario.post(url, {
            'user_id': user_collaboratore.id
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert not progetto.collaboratori.filter(id=user_collaboratore.id).exists()

    @pytest.mark.negativo
    def test_collaboratore_non_puo_aggiungere_collaboratore(self, client_collaboratore, progetto, user_estraneo):
        url = reverse('projects-add-collaborator', args=[progetto.id])
        response = client_collaboratore.post(url, {
            'user_id': user_estraneo.id
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.negativo
    def test_add_collaborator_user_non_esiste(self, client_proprietario, progetto):
        url = reverse('projects-add-collaborator', args=[progetto.id])
        response = client_proprietario.post(url, {
            'user_id': 9999
        }, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND