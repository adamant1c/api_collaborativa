from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Collaborativa",
        default_version='v1',
        description="Documentazione di API collaborativa con l'elenco degli handler disponibili",
        contact=openapi.Contact(email="alessandro.perotti@yahoo.it"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='http://localhost:8000/api/',  # oppure il dominio reale in produzione
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('autenticazione.urls')),
    path('api/', include('progetti.urls')),
    re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]