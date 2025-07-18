from django.db import models
from django.contrib.auth.models import User
import logging
from django.utils import timezone
from django.db.models import CharField


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

    def __str__(self) -> CharField:
        return self.nome

    def percentuale_completamento(self):
        """Calcola la percentuale di task completati"""
        task_totali = self.tasks.count()
        if task_totali == 0:
            logging.warning("Non ci sono ancora tasks nel progetto!")
            return 0
        done_tasks = self.tasks.filter(stato='DONE').count()
        return round((done_tasks / task_totali) * 100, 1)

    def is_member(self, user) -> bool:
        """Verifica se un utente è proprietario oppure è contenuto nella lista collaboratori
        :param: istanza dell'utente che fa la request
        :return: True se l'utente è proprietario o è nella lista collaboratori, False in caso contrario
        """

        if user == self.proprietario or user in self.collaboratori.all():
            logging.debug("Utente è proprietario oppure è contenuto nella lista collaboratori")
            return True
        else:
            logging.warning("Utente non autorizzato")
            return False


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
    assegnatario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assegnati',
        verbose_name="Assegnato a"
    )
    autore = models.ForeignKey(
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

    def __str__(self) -> str:
        return f"{self.titolo} - {self.progetto.nome}"

    def check_ritardo(self):
        """Verifica se il task è in ritardo"""

        if self.scadenza and self.stato != 'DONE':
            return timezone.now() > self.scadenza
        return False