import pytest
from django.urls import reverse
from rest_framework import status

from progetti.models import Progetto

@pytest.mark.django_db
class TestProgettoViewSet:
    @pytest.mark.positivo
    def test_proprietario_puo_creare_progetto(self, client_autenticato):
        url = reverse('projects-list')
        response = client_autenticato.post(url, {
            'nome': 'Nuovo Progetto',
            'descrizione': 'Descrizione test'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == 'Nuovo Progetto'

    @pytest.mark.positivo
    def test_collaboratore_puo_leggere_progetto(self, client_collaboratore, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == progetto.id

    @pytest.mark.negativo
    def test_estraneo_non_puo_leggere_progetto(self, client_estraneo, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_estraneo.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_proprietario_puo_aggiornare_progetto(self, client_autenticato, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_autenticato.patch(url, {'nome': 'Nome aggiornato'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == 'Nome aggiornato'

    @pytest.mark.negativo
    def test_collaboratore_non_puo_aggiornare_progetto(self, client_collaboratore, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.patch(url, {'nome': 'Non valido'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_proprietario_puo_eliminare_progetto(self, client_autenticato, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_autenticato.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Progetto.objects.filter(id=progetto.id).exists()

    @pytest.mark.negativo
    def test_collaboratore_non_puo_eliminare_progetto(self, client_collaboratore, progetto):
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_list_progetti_filtrati_per_membro(self, client_collaboratore, progetto):
        url = reverse('projects-list')
        response = client_collaboratore.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(p['id'] == progetto.id for p in response.data)
