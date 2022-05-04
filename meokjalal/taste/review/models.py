from django.conf import settings
from django.db import models
# Create your models here.


class Review(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='review')
    content = models.TextField(max_length=400)
    service = models.IntegerField(null=False, blank=False)
    taste = models.IntegerField(null=False, blank=False)
    clean = models.IntegerField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return f'Review (PK: {self.pk}, Author: {self.author.username})'


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'Comment (PK: {self.pk}, Author: {self.author.username})'