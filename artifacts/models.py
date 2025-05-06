from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, SmartResize

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followers')
    blocked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='blocked_by')
    blocked_tags = models.ManyToManyField(Tag, blank=True, related_name='blocked_by')
    blocked_categories = models.ManyToManyField(Category, blank=True, related_name='blocked_by')
    bio = models.TextField(blank=True, help_text="Tell others about yourself")
    website = models.URLField(blank=True)
    avatar = ProcessedImageField(upload_to='avatars/',
                               processors=[SmartResize(200, 200)],
                               format='JPEG',
                               options={'quality': 85},
                               blank=True,
                               null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def is_following(self, user):
        return self.following.filter(id=user.id).exists()

    def is_blocking(self, user):
        return self.blocked_users.filter(id=user.id).exists()

    def follow(self, user):
        if not self.is_blocking(user) and user != self.user:
            self.following.add(user)
            self.save()

    def unfollow(self, user):
        self.following.remove(user)
        self.save()

    def block(self, user):
        self.blocked_users.add(user)
        self.following.remove(user)  # Automatically unfollow when blocking
        self.save()

    def unblock(self, user):
        self.blocked_users.remove(user)
        self.save()

class Artifact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artifacts', null=True)
    title = models.CharField(max_length=200)
    description = CKEditor5Field(config_name='extends', blank=True)
    # Main display image with automatic resizing
    image = ProcessedImageField(upload_to='artifacts/',
                              processors=[ResizeToFit(1200, 1200)],
                              format='JPEG',
                              options={'quality': 85},
                              blank=True,
                              null=True)
    # Thumbnail for grid views
    thumbnail = ProcessedImageField(upload_to='artifacts/thumbnails/',
                                  processors=[SmartResize(400, 400)],
                                  format='JPEG',
                                  options={'quality': 80},
                                  blank=True,
                                  null=True)
    popularity_score = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='artifacts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='artifacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.user.username if self.user else 'unknown'}"

    def save(self, *args, **kwargs):
        # Generate thumbnail from main image if not provided
        if self.image and not self.thumbnail:
            self.thumbnail = self.image
        super().save(*args, **kwargs)

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', null=True)
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name='comments')
    text = CKEditor5Field(config_name='extends', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username if self.user else "unknown"} on {self.artifact.title}'
