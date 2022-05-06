from django.urls import path, re_path

from . import views


app_name = 'store'

urlpatterns = [
    path('map/', views.taste_map, name='taste_map'),
]