from rest_framework import permissions
from .models import Progetto
import logging
class IsProjectOwner(permissions.BasePermission):
    """
    Permesso personalizzato per verificare se l'utente è il proprietario del progetto.
    Solo il proprietario può modificare/eliminare il progetto.
    """

    def has_object_permission(self, request, view, obj):
        """ Verifico chi ha i permessi per modificare il progetto oppure solo leggerne i dati"""
        # Permessi di lettura per tutti i membri del progetto
        if request.method in permissions.SAFE_METHODS:
            return obj.is_member(request.user)

        # Permessi di scrittura solo per il proprietario
        return obj.proprietario == request.user


class IsProjectMember(permissions.BasePermission):
    """
    Permesso per verificare se l'utente è membro del progetto.
    Proprietario e collaboratori possono accedere.
    """

    def has_object_permission(self, request, view, obj):
        # Per i progetti
        if hasattr(obj, 'proprietario'):
            return obj.is_member(request.user)

        # Per i task - verifico se l'utente è membro del progetto
        if hasattr(obj, 'progetto'):
            return obj.progetto.is_member(request.user)

        return False

class CanModifyTask(permissions.BasePermission):
    """
    Permesso per i tasks.
    - Proprietario del progetto: può tutto
    - Collaboratori: possono creare/modificare task
    - Creatore del task: può sempre modificare il suo task
    """

    def has_permission(self, request, view):
        # Per la creazione di task, verifico se l'utente è membro del progetto
        if request.method == 'POST':
            project_id = request.data.get('progetto')
            if project_id:
                try:

                    progetto = Progetto.objects.get(id=project_id)
                    return progetto.is_member(request.user)
                except Progetto.DoesNotExist:
                    logging.warning("Il progetto richiesto non esiste nel Database")
                    return False
        return True

    def has_object_permission(self, request, view, obj):
        # Lettura: tutti i membri del progetto
        if request.method in permissions.SAFE_METHODS:
            return obj.progetto.is_member(request.user)

        # Modifica/Eliminazione:
        # 1. Proprietario del progetto
        # 2. Creatore del task
        # 3. Collaboratori possono modificare (ma non eliminare)
        if request.method == 'DELETE':
            return (obj.progetto.proprietario == request.user or
                    obj.autore == request.user)

        # Per PUT/PATCH
        return (obj.progetto.proprietario == request.user or
                obj.autore == request.user or
                request.user in obj.progetto.collaboratori.all())


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permesso generico: il proprietario può modificare, altri solo leggere.
    """

    def has_object_permission(self, request, view, obj):
        # Permessi di lettura per tutti gli utenti autenticati
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permessi di scrittura solo per il proprietario
        return obj.proprietario == request.user if hasattr(obj, 'proprietario') else False
