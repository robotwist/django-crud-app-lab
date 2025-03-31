from django.db import models

class Artifact(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    popularity_score = models.IntegerField(default=0)  # 💥 New!
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
