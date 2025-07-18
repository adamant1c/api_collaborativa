from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Progetto, Task


class UserSerializer(serializers.ModelSerializer):
    """Serializer per gli utenti"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer per i task con informazioni dettagliate"""

    autore = UserSerializer(read_only=True)
    assegnatario = UserSerializer(read_only=True)
    assigned_to_id  = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    check_ritardo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'titolo', 'descrizione', 'progetto', 'stato',
            'scadenza', 'autore', 'assegnatario', 'assigned_to_id',
            'check_ritardo', 'data_creazione', 'data_aggiornamento'
        ]
        read_only_fields = ['id', 'autore', 'data_creazione', 'data_aggiornamento']

    def validate_assigned_to_id(self, value):
        """Verifica che l'utente assegnato sia membro del progetto"""
        if value is not None:
            progetto = self.context.get('progetto')
            if progetto:
                try:
                    user = User.objects.get(id=value)
                    if not progetto.is_member(user):
                        raise serializers.ValidationError(
                            "L'utente deve essere membro del progetto"
                        )
                except User.DoesNotExist:
                    raise serializers.ValidationError("Utente non trovato")
        return value

    def create(self, validated_data):
        """Crea un task assegnando automaticamente il autore"""
        assigned_to_id = validated_data.pop('assigned_to_id', None)

        # Assegna automaticamente l'utente che crea il task
        validated_data['autore'] = self.context['request'].user

        # Gestisce l'assegnazione
        if assigned_to_id:
            validated_data['assigned_to_id'] = assigned_to_id

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Aggiorna un task gestendo l'assegnazione"""
        assigned_to_id = validated_data.pop('assigned_to_id', None)

        if assigned_to_id is not None:
            if assigned_to_id:
                instance.assigned_to_id = assigned_to_id
            else:
                instance.assigned_to = None

        return super().update(instance, validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer per i progetti"""

    proprietario = UserSerializer(read_only=True)
    collaboratori = UserSerializer(many=True, read_only=True)
    id_collaboratori = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    # Statistiche
    percentuale_completamento = serializers.FloatField(read_only=True)
    task_totali = serializers.IntegerField(read_only=True)
    done_tasks = serializers.IntegerField(read_only=True)


    class Meta:
        model = Progetto
        fields = [
            'id', 'nome', 'descrizione', 'proprietario', 'collaboratori',
            'id_collaboratori', 'percentuale_completamento', 'task_totali',
            'done_tasks', 'data_creazione', 'data_aggiornamento'
        ]
        read_only_fields = ['id', 'proprietario', 'data_creazione', 'data_aggiornamento']

    def validate_collaborator_ids(self, value):
        """Verifica che gli ID dei collaboratori siano validi"""
        if value:
            users = User.objects.filter(id__in=value)
            if len(users) != len(value):
                raise serializers.ValidationError(
                    "Alcuni utenti non sono stati trovati"
                )

        return value

    def create(self, validated_data):
        """Crea un progetto assegnando automaticamente il proprietario"""
        id_collaboratori = validated_data.pop('id_collaboratori', [])

        # Assegna automaticamente il proprietario
        validated_data['proprietario'] = self.context['request'].user

        progetto = super().create(validated_data)

        # Aggiunge i collaboratori
        if id_collaboratori:
            collaboratori = User.objects.filter(id__in=id_collaboratori)
            progetto.collaboratori.set(collaboratori)

        return progetto

    def update(self, instance, validated_data):
        """Aggiorna un progetto gestendo i collaboratori"""
        id_collaboratori = validated_data.pop('id_collaboratori', None)

        progetto = super().update(instance, validated_data)

        # Aggiorna i collaboratori se specificati
        if id_collaboratori is not None:
            collaboratori = User.objects.filter(id__in=id_collaboratori)
            progetto.collaboratori.set(collaboratori)

        return progetto


class ProjectStatsSerializer(serializers.ModelSerializer):
    """Serializer per le statistiche del progetto"""

    percentuale_completamento = serializers.FloatField(read_only=True)
    task_totali = serializers.IntegerField(read_only=True)
    done_tasks = serializers.IntegerField(read_only=True)
    in_progress_tasks = serializers.IntegerField(read_only=True)
    todo_tasks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Progetto
        fields = [
            'id', 'nome', 'percentuale_completamento', 'task_totali',
            'done_tasks', 'in_progress_tasks', 'todo_tasks'
        ]