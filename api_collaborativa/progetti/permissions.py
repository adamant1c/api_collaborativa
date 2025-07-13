# projects/permissions.py
from rest_framework import permissions


class IsProjectOwner(permissions.BasePermission):
    """
    Permesso personalizzato per verificare se l'utente è il proprietario del progetto.
    Solo il proprietario può modificare/eliminare il progetto.
    """

    def has_object_permission(self, request, view, obj):
        # Permessi di lettura per tutti i membri del progetto
        if request.method in permissions.SAFE_METHODS:
            return obj.is_member(request.user)

        # Permessi di scrittura solo per il proprietario
        return obj.owner == request.user
