from django.db import models

# Create your models here.
# class Store(models.Model):

class Store(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False)
    s_name = models.TextField(null=True)
    s_add = models.TextField(null=True)
    s_road = models.TextField(null=True)
    s_kind = models.TextField(null=True)
    lat = models.FloatField(null=True)
    lot = models.FloatField(null=True)
    s_status = models.TextField(null=True)
    modification_time = models.DateTimeField(null=True)

    # class Meta:
    #     db_table = 'store_store'

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

    # class Meta:
    #     db_table = 'store_detail'

    def __str__(self):
        return f'Detail (PK: {self.pk})'


# 날씨 데이터 테이블
class Weather(models.Model):
    id = models.IntegerField(primary_key=True)
    fcstDate = models.TextField(blank=True, null=True)
    fcstTime = models.TextField(blank=True, null=True)
    temp = models.TextField(blank=True, null=True)
    cloud = models.TextField(blank=True, null=True)
    rain = models.TextField(blank=True, null=True)
