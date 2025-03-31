from django.urls import path
from . import views

urlpatterns = [
    path('', views.artifact_list, name='artifact_list'),
    path('<int:pk>/', views.artifact_detail, name='artifact_detail'),
    path('create/', views.artifact_create, name='artifact_create'),
    path('<int:pk>/update/', views.artifact_update, name='artifact_update'),
    path('<int:pk>/delete/', views.artifact_delete, name='artifact_delete'),
    path('<int:pk>/like/', views.artifact_like, name='artifact_like'),

]
