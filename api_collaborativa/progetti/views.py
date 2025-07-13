from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from django.contrib.auth.models import User
import logging

from rest_framework.views import APIView

from .models import Progetto, Task
from .serializers import (
    ProjectSerializer, TaskSerializer, ProjectStatsSerializer,
    UserSerializer
)
from .permissions import IsProjectOwner, IsProjectMember, CanModifyTask

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet per gestire i progetti.
    """

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restituisce solo i progetti dove l'utente è owner o collaboratore.
        Aggiunge anche le statistiche.
        """
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
        Permessi diversi per azioni diverse.
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
        Aggiunge un collaboratore al progetto.
        Solo il proprietario può farlo.
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


            if user in progetto.collaborators.all():
                logging.error("Utente già collaboratore")
                return Response(
                    {'error': 'Utente già collaboratore'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            progetto.collaborators.add(user)
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
        Rimuove un collaboratore dal progetto.
        Solo il proprietario può farlo.
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

            if user not in progetto.collaborators.all():
                logging.error("Utente non è collaboratore")
                return Response(
                    {'error': 'Utente non è collaboratore'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            progetto.collaborators.remove(user)
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

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Restituisce statistiche dettagliate del progetto.
        """
        project = self.get_object()
        serializer = ProjectStatsSerializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Restituisce tutti i task del progetto.
        """
        project = self.get_object()
        tasks = project.tasks.all().select_related('assegnatario', 'autore')

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet per gestire i task.
    Permessi: solo membri del progetto possono vedere/modificare.
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanModifyTask]

    def get_queryset(self):
        """
        Restituisce solo i task dei progetti dove l'utente è membro.
        """
        user = self.request.user
        return Task.objects.filter(
            Q(progetto__proprietario=user) | Q(progetto__collaboratori=user)
        ).select_related(
            'progetto', 'assegnatario', 'autore'
        ).distinct()

    def get_serializer_context(self):
        """Aggiunge il progetto al context del serializer"""
        context = super().get_serializer_context()
        if hasattr(self, 'request') and self.request.data.get('progetto'):
            try:
                from .models import Project
                project = Project.objects.get(id=self.request.data['progetto'])
                context['progetto'] = project
            except Project.DoesNotExist:
                pass
        return context

    def perform_create(self, serializer):
        """Assegna automaticamente il created_by al task"""
        serializer.save(created_by=self.request.user)


class StatsView(APIView):
    """
    Vista per statistiche generali dell'utente.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Progetti dell'utente
        owned_projects = Progetto.objects.filter(proprietario=user).count()
        collaborative_projects = Progetto.objects.filter(collaboratori=user).count()

        # Task dell'utente
        assigned_tasks = Task.objects.filter(assegnatario=user)
        total_assigned = assigned_tasks.count()
        completed_assigned = assigned_tasks.filter(stato='DONE').count()

        # Task creati dall'utente
        created_tasks = Task.objects.filter(autore=user).count()

        # Statistiche per progetto (solo progetti dove l'utente è proprietario o collaboratore)
        user_projects = Progetto.objects.filter(
            Q(proprietario=user) | Q(collaboratori=user)
        ).distinct()

        project_stats = []
        for project in user_projects:
            total_tasks = project.tasks.count()
            completed_tasks = project.tasks.filter(stato='DONE').count()
            in_progress_tasks = project.tasks.filter(stato='IN_PROGRESS').count()
            todo_tasks = project.tasks.filter(stato='TODO').count()

            completion_rate = round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                1
            )

            project_stats.append({
                'project_id': project.id,
                'project_name': project.nome,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'todo_tasks': todo_tasks,
                'completion_rate': completion_rate,
                'is_owner': project.proprietario == user
            })

        # Statistiche generali sui task per stato
        user_task_stats = Task.objects.filter(
            Q(assegnatario=user) | Q(autore=user)
        ).values('stato').annotate(count=Count('id'))

        task_by_status = {
            'TODO': 0,
            'IN_PROGRESS': 0,
            'DONE': 0
        }

        for stat in user_task_stats:
            task_by_status[stat['stato']] = stat['count']

        data = {
            'projects': {
                'owned': owned_projects,
                'collaborative': collaborative_projects,
                'total': owned_projects + collaborative_projects,
            },
            'tasks': {
                'assigned_total': total_assigned,
                'assigned_completed': completed_assigned,
                'created_total': created_tasks,
                'by_status': task_by_status
            },
            'completion_rate': round(
                (completed_assigned / total_assigned * 100) if total_assigned > 0 else 0,
                1
            ),
            'project_statistics': project_stats
        }

        return Response(data)