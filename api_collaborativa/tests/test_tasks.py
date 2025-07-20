import pytest
from django.urls import reverse
from rest_framework import status

from progetti.models import Task

@pytest.mark.django_db
class TestTaskViewSet:
    @pytest.mark.positivo
    def test_owner_puo_creare_task(self, client_autenticato, progetto):
        url = reverse('tasks-list')
        response = client_autenticato.post(url, {
            'titolo': 'Task 1',
            'descrizione': 'Descrizione task',
            'progetto': progetto.id,
            'stato': 'TODO'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['titolo'] == 'Task 1'

    @pytest.mark.positivo
    def test_collaboratore_puo_creare_task(self, client_collaboratore, progetto):
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
        url = reverse('tasks-list')
        response = client_estraneo.post(url, {
            'titolo': 'Task vietato',
            'progetto': progetto.id,
            'stato': 'TODO'
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_owner_puo_modificare_task(self, client_autenticato, task):
        url = reverse('tasks-detail', args=[task.id])
        response = client_autenticato.patch(url, {
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
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.negativo
    def test_collaboratore_non_puo_eliminare_task_non_suo(self, client_collaboratore, task):
        url = reverse('tasks-detail', args=[task.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_autore_puo_eliminare_task_proprio(self, user_collaboratore, client_collaboratore, progetto):
        task = Task.objects.create(
            titolo='Creato da collab',
            progetto=progetto,
            autore=user_collaboratore
        )
        url = reverse('tasks-detail', args=[task.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.positivo
    def test_owner_puo_aggiungere_collaboratore(self, client_autenticato, progetto, user_estraneo):
        url = reverse('progetto-add-collaborator', args=[progetto.id])
        response = client_autenticato.post(url, {
            'user_id': user_estraneo.id
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert progetto.collaboratori.filter(id=user_estraneo.id).exists()

    @pytest.mark.positivo
    def test_owner_puo_rimuovere_collaboratore(self, client_autenticato, progetto, user_collaboratore):
        url = reverse('progetto-remove-collaborator', args=[progetto.id])
        response = client_autenticato.post(url, {
            'user_id': user_collaboratore.id
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert not progetto.collaboratori.filter(id=user_collaboratore.id).exists()

    @pytest.mark.negativo
    def test_collaboratore_non_puo_aggiungere_collaboratore(self, client_collaboratore, progetto, user_estraneo):
        url = reverse('progetto-add-collaborator', args=[progetto.id])
        response = client_collaboratore.post(url, {
            'user_id': user_estraneo.id
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.negativo
    def test_add_collaborator_user_non_esiste(self, client_autenticato, progetto):
        url = reverse('progetto-add-collaborator', args=[progetto.id])
        response = client_autenticato.post(url, {
            'user_id': 9999
        }, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND