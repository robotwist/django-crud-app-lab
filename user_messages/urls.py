from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # Conversations
    path('', views.conversation_list, name='conversation_list'),
    path('new/', views.start_conversation, name='start_conversation'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    
    # Messages within conversations
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('<int:conversation_id>/messages/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
] 