from django.contrib import admin
from .models import Progetto, Task

@admin.register(Progetto)
class ProgettoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'proprietario', 'data_creazione', 'data_aggiornamento')
    search_fields = ('nome', 'descrizione')
    list_filter = ('data_creazione',)
    filter_horizontal = ('collaboratori',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'progetto', 'stato', 'assegnatario', 'scadenza', 'data_creazione')
    search_fields = ('titolo', 'descrizione')
    list_filter = ('stato', 'scadenza', 'data_creazione')

