from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Progetto(models.Model):
    """
    Modello per i progetti.
    Ogni progetto ha un proprietario e può avere collaboratori.
    """
    nome = models.CharField(max_length=200, verbose_name="Nome del Progetto")
    descrizione = models.TextField(blank=True, verbose_name="Descrizione del Progetto")
    proprietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proprietario_progetti',
        verbose_name="Proprietario"
    )
    collaboratori = models.ManyToManyField(
        User,
        blank=True,
        related_name='collaboratori_progetti',
        verbose_name="Collaboratori"
    )
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_creazione']
        verbose_name = "Progetto"
        verbose_name_plural = "Progetti"

    def __str__(self):
        return self.nome

    def statistiche(self):
        """Calcola la percentuale di task completati"""
        task_totali = self.tasks.count()
        if task_totali == 0:
            return 0
        task_completati = self.tasks.filter(status='DONE').count()
        return round((task_completati / task_totali) * 100, 1)

    def is_member(self, user):
        """Verifica se un utente è proprietario oppure è contenuto nella lista collaboratore"""
        return user == self.proprietario or user in self.collaboratori.all()


class Task(models.Model):
    """
    Modello per i tasks.
    Ogni tasks appartiene a un progetto e ha stati definiti.
    """

    STATUS_CHOICES = [
        ('TODO', 'Da Fare'),
        ('IN_PROGRESS', 'In Corso'),
        ('DONE', 'Completato'),
    ]


    titolo = models.CharField(max_length=200, verbose_name="Titolo")
    descrizione = models.TextField(blank=True, verbose_name="Descrizione")
    progetto = models.ForeignKey(
        Progetto,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Progetto"
    )
    assegnato = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assegnati',
        verbose_name="Assegnato a"
    )
    creato_da = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_creati',
        verbose_name="Creato da"
    )
    stato = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO',
        verbose_name="Stato"
    )

    scadenza = models.DateTimeField(null=True, blank=True, verbose_name="Scadenza")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_creazione']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.titolo} - {self.progetto.nome}"

    def check_ritardo(self):
        """Verifica se il task è in ritardo"""
        from django.utils import timezone
        if self.scadenza and self.stato != 'DONE':
            return timezone.now() > self.scadenza
        return False