from django.db import models

# Create your models here.
# class Store(models.Model):

class Store(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False)
    s_name = models.TextField()
    s_add = models.TextField(null=True)
    s_road = models.TextField()
    s_kind = models.TextField()
    lat = models.FloatField()
    lot = models.FloatField()
    s_status = models.TextField()
    modification_time = models.DateTimeField()

    def __str__(self):
        return f'Store (PK: {self.pk})'       


class Detail(models.Model):
    id = models.IntegerField(primary_key=True)
    s_name = models.TextField(blank=True, null=True)
    s_tel = models.TextField(blank=True, null=True)
    s_photo = models.TextField(blank=True, null=True)
    s_hour = models.TextField(blank=True, null=True)
    s_etc = models.TextField(blank=True, null=True)
    s_menu = models.TextField(blank=True, null=True)
    s_price = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'Detail (PK: {self.pk})'