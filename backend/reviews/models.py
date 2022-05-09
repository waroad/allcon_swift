from django.db import models


class Review(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    star = models.IntegerField(default=10)
    owner = models.ForeignKey('auth.User', related_name='owner_review', on_delete=models.CASCADE)
    movieId = models.ForeignKey('movies.Movie', related_name='review_movie_id', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-createdAt']
