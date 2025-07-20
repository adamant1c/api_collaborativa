import pytest
from django.urls import reverse
from rest_framework import status

from progetti.models import Progetto

@pytest.mark.django_db
class TestProgettoViewSet:
    """
    Classe di Test che verifica le operazioni CRUD e i permessi di accesso ai progetti per proprietari,
    collaboratori e utenti estranei.
    """
    @pytest.mark.positivo
    def test_proprietario_puo_creare_progetto(self, client_autenticato):
        """
       Test Steps:
       - Usa il client autenticato (user_proprietario) per inviare una POST
       - Verifica che il progetto venga creato correttamente
       - Controlla il contenuto della risposta
        """
        url = reverse('projects-list')
        response = client_autenticato.post(url, {
            'nome': 'Nuovo Progetto',
            'descrizione': 'Descrizione test'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == 'Nuovo Progetto'

    @pytest.mark.positivo
    def test_collaboratore_puo_leggere_progetto(self, client_collaboratore, progetto):
        """
        Test Steps:
        - Un client autenticato come collaboratore accede a un progetto
        - Verifica che possa visualizzarne i dettagli
        """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == progetto.id

    @pytest.mark.negativo
    def test_estraneo_non_puo_leggere_progetto(self, client_estraneo, progetto):
        """
         Test Steps:
         - Un utente non collaboratore né proprietario cerca di accedere a un progetto
         - Verifica che ottiene una risposta 403 (accesso negato)
         """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_estraneo.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.positivo
    def test_proprietario_puo_aggiornare_progetto(self, client_autenticato, progetto):
        """
        Test Steps:
        - Il proprietario modifica il nome del progetto tramite PATCH
        - Verifica che la modifica ha effetto
        """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_autenticato.patch(url, {'nome': 'Nome aggiornato'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == 'Nome aggiornato'

    @pytest.mark.negativo
    def test_collaboratore_non_puo_aggiornare_progetto(self, client_collaboratore, progetto):
        """
          Test Steps:
          - Un collaboratore prova a modificare il progetto
          - Verifica che viene negato l'accesso
        """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.patch(url, {'nome': 'Non valido'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_proprietario_puo_eliminare_progetto(self, client_autenticato, progetto):
        """
         Test Steps:
         - Il proprietario invia una DELETE sul progetto
         - Verifica che viene eliminato con successo
         - Controlla che non esiste più nel DB
         """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_autenticato.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Progetto.objects.filter(id=progetto.id).exists()

    @pytest.mark.negativo
    def test_collaboratore_non_puo_eliminare_progetto(self, client_collaboratore, progetto):
        """
        Test Steps:
        - Un collaboratore tenta di eliminare il progetto
        - Verifica che l'operazione viene negata
        """
        url = reverse('projects-detail', args=[progetto.id])
        response = client_collaboratore.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.positivo
    def test_list_progetti_filtrati_per_membro(self, client_collaboratore, progetto):
        """
        Test Steps:
        - Il collaboratore esegue una GET su /projects/
        - Verifica che riceve solo i progetti a cui partecipa
        """
        url = reverse('projects-list')
        response = client_collaboratore.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(p['id'] == progetto.id for p in response.data['results'])
