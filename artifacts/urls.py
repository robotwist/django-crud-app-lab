from django.urls import path
from . import views

urlpatterns = [
    path('', views.artifact_list, name='artifact_list'),
    path('feed/', views.user_feed, name='user_feed'),
    path('<int:pk>/', views.artifact_detail, name='artifact_detail'),
    path('create/', views.artifact_create, name='artifact_create'),
    path('<int:pk>/update/', views.artifact_update, name='artifact_update'),
    path('<int:pk>/delete/', views.artifact_delete, name='artifact_delete'),
    path('<int:pk>/like/', views.artifact_like, name='artifact_like'),
    
    # User profiles and preferences
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('preferences/', views.user_preferences, name='user_preferences'),
    
    # Follow/unfollow
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('user/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    
    # Block/unblock
    path('user/<str:username>/block/', views.block_user, name='block_user'),
    path('user/<str:username>/unblock/', views.unblock_user, name='unblock_user'),
]
