from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Case, When, IntegerField
from django.contrib.auth.models import User
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

from .models import Progetto, Task
from .serializers import (
    ProjectSerializer, TaskSerializer, ProjectStatsSerializer,
    UserSerializer
)
from .permissions import IsProjectOwner, IsProjectMember, CanModifyTask

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API per la gestione dei progetti.

    ## Endpoint disponibili

    - `GET /projects/` — lista progetti dell’utente
    - `POST /projects/` — crea un nuovo progetto

    ### Body JSON per creazione progetto (POST)
    ```json
    {
        "nome": "Nome progetto",
        "descrizione": "Descrizione",
        "id_collaboratori": [1, 2]
    }
    ```

    - `nome` e `descrizione` sono obbligatori
    - `id_collaboratori` è facoltativo (array di ID utente)
    - `proprietario`, `collaboratori`, `task_totali` e `done_tasks` sono calcolati e non devono essere inviati
    """

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
          Restituisce i progetti in cui l'utente autenticato è:

          - proprietario (`proprietario`)
          - o collaboratore (`collaboratori`)

          Ogni progetto viene annotato con statistiche relative ai task:
          - task_totali
          - done_tasks
          - in_progress_tasks
          - todo_tasks

          ## Nota
          Se `swagger_fake_view` è attivo (durante la generazione dello schema), viene restituito un queryset vuoto.
          """
        if getattr(self, 'swagger_fake_view', False):
            return Progetto.objects.none()


        user = self.request.user
        return Progetto.objects.filter(
            Q(proprietario=user) | Q(collaboratori=user)
        ).annotate(
            task_totali=Count('tasks'),
            done_tasks=Count(
                Case(
                    When(tasks__stato='DONE', then=1),
                    output_field=IntegerField()
                )
            ),
            in_progress_tasks=Count(
                Case(
                    When(tasks__stato='IN_PROGRESS', then=1),
                    output_field=IntegerField()
                )
            ),
            todo_tasks=Count(
                Case(
                    When(tasks__stato='TODO', then=1),
                    output_field=IntegerField()
                )
            )
        ).prefetch_related(
            'collaboratori',
            'proprietario'
        ).distinct()

    def get_permissions(self):
        """
        Applica permessi diversi in base all'azione eseguita:

        - `update`, `partial_update`, `destroy`, `add_collaborator`, `remove_collaborator`:
          Richiede essere proprietario del progetto (`IsProjectOwner`)
        - `list`, `retrieve`:
          Richiede essere membro del progetto (`IsProjectMember`)
        - Altrimenti:
          Autenticazione base
        """
        if self.action in ['update', 'partial_update', 'destroy', 'add_collaborator', 'remove_collaborator']:
            permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Assegna automaticamente il proprietario al progetto"""
        serializer.save(proprietario=self.request.user)

    @action(detail=True, methods=['post'])
    def add_collaborator(self, request, pk=None):
        """
        Aggiunge un collaboratore a un progetto esistente.

        ## Metodo
        POST

        ## Permessi
        Solo il proprietario del progetto può eseguire questa azione.

        ## Body JSON
        - **user_id**: ID dell'utente da aggiungere come collaboratore

        ## Risposte
        - 200: Collaboratore aggiunto
        - 400: Errore di validazione (es. già collaboratore o user_id mancante)
        - 404: Utente non trovato
        """
        progetto = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            logging.error("user_id è richiesto")
            return Response(
                {'error': 'user_id è richiesto'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)


            if user in progetto.collaboratori.all():
                logging.error("Utente già collaboratore")
                return Response(
                    {'error': 'Utente già collaboratore'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            progetto.collaboratori.add(user)
            logging.info(f"Collaboratore {user.username} aggiunto con successo")
            return Response(
                {'message': f'Collaboratore {user.username} aggiunto con successo'},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            logging.error("Utente non trovato")
            return Response(
                {'error': 'Utente non trovato'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_collaborator(self, request, pk=None):
        """
        Rimuove un collaboratore da un progetto.

        ## Metodo
        POST

        ## Permessi
        Solo il proprietario del progetto può eseguire questa azione.

        ## Body JSON
        - **user_id**: ID dell'utente da rimuovere

        ## Risposte
        - 200: Collaboratore rimosso
        - 400: Utente non collaboratore o `user_id` mancante
        - 404: Utente non trovato
        """
        progetto = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            logging.error("user_id è richiesto")
            return Response(
                {'error': 'user_id è richiesto'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)

            if user not in progetto.collaboratori.all():
                logging.error("Utente non è collaboratore")
                return Response(
                    {'error': 'Utente non è collaboratore'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            progetto.collaboratori.remove(user)
            logging.info( f'Collaboratore {user.username} rimosso con successo')
            return Response(
                {'message': f'Collaboratore {user.username} rimosso con successo'},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            logging.error("Utente non trovato")
            return Response(
                {'error': 'Utente non trovato'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        method='get',
        operation_summary="Statistiche progetto",
        operation_description="Restituisce le statistiche dettagliate per un progetto specifico.",
        responses={200: ProjectStatsSerializer()}
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
          Restituisce le statistiche dettagliate del progetto.

          Include il numero di task per stato (TODO, IN_PROGRESS, DONE), e altri dati aggregati.
        """
        project = self.get_object()
        serializer = ProjectStatsSerializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Restituisce tutti i task associati al progetto specificato.

        I task includono i dettagli di autore e assegnatario.
        """
        project = self.get_object()
        tasks = project.tasks.all().select_related('assegnatario', 'autore')

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API per la gestione dei task.

    Permette di creare, aggiornare, visualizzare e cancellare task.
    L'accesso è limitato ai membri del progetto a cui il task appartiene.
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanModifyTask]

    def get_queryset(self):
        """
        Restituisce solo i task appartenenti a progetti dove l'utente autenticato è:

        - Proprietario (`proprietario`)
        - o Collaboratore (`collaboratori`)

        I task includono i dettagli del progetto, autore e assegnatario.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()

        user = self.request.user
        return Task.objects.filter(
            Q(progetto__proprietario=user) | Q(progetto__collaboratori=user)
        ).select_related(
            'progetto', 'assegnatario', 'autore'
        ).distinct()

    def get_serializer_context(self):
        """
        Aggiunge il progetto al context del serializer, se fornito nel payload.

        Utile per validazioni o logica personalizzata all'interno del serializer.
        """
        context = super().get_serializer_context()
        if hasattr(self, 'request') and self.request.data.get('progetto'):
            try:

                project = Progetto.objects.get(id=self.request.data['progetto'])
                context['progetto'] = project
            except Progetto.DoesNotExist:
                pass
        return context

    def perform_create(self, serializer):
        """
        Imposta automaticamente l'utente autenticato come autore  del task.
        """
        serializer.save(autore=self.request.user)
