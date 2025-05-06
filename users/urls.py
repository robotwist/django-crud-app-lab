from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    
    # User profiles
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    
    # Friends
    path('friends/', views.friend_list, name='friend_list'),
    path('friends/requests/', views.friend_requests, name='friend_requests'),
    path('friends/add/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<str:username>/', views.remove_friend, name='remove_friend'),
] 