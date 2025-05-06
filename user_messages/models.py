from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """A conversation between two or more users"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.id} ({', '.join([user.username for user in self.participants.all()])})"
    
    def get_latest_message(self):
        return self.messages.order_by('-created_at').first()
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    """Individual message within a conversation"""
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['created_at']

class Notification(models.Model):
    """Notification system for various events"""
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('friend_request', 'Friend Request'),
        ('trade_offer', 'Trade Offer'),
        ('trade_status', 'Trade Status Update'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    related_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
