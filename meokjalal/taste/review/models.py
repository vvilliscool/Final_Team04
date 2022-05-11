from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms


# Create your models here.

CHOICES = [(1,'★'),(2,'★'),(3,'★'),(4,'★'),(5,'★')]
class Review(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='review')
    content = models.TextField(max_length=400)
    service = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    taste = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    cleaned = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    price = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE)

    def __str__(self):
        return f'Review (PK: {self.pk}, Author: {self.author.username})'


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'Comment (PK: {self.pk}, Author: {self.author.username})'