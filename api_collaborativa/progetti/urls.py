from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router per ViewSets
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='projects')
router.register(r'tasks', views.TaskViewSet, basename='tasks')



urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
