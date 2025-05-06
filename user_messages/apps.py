from django.apps import AppConfig


class UserMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_messages'
    verbose_name = 'User Messages'  # To differentiate from Django's messages module
