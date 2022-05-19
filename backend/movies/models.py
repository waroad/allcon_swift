from django.db import models


class Movie(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    liker = models.ManyToManyField('auth.user', related_name='liker_movie')
    liked = models.IntegerField(default=0)
    likeCount = models.IntegerField(default=0)
    currentUser = models.TextField(default="None")

    class Meta:
        ordering = ['-createdAt']
