from django.contrib.auth.models import AbstractUser
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.conf import settings

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = ProcessedImageField(upload_to='avatars/',
                               processors=[ResizeToFit(300, 300)],
                               format='JPEG',
                               options={'quality': 85},
                               blank=True,
                               null=True)
    website = models.URLField(max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username

class Friendship(models.Model):
    """Model to handle friend relationships between users"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friendships', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friendships', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')
    
    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"

    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            (models.Q(sender=user1, receiver=user2) | 
             models.Q(sender=user2, receiver=user1)),
            status='accepted'
        ).exists()
