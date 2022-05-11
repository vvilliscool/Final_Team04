from django.urls import path, re_path

from . import views


app_name = 'store'

urlpatterns = [
    path('map/', views.taste_map, name='taste_map'),
    path('theme/', views.theme, name='theme'),
    path('theme/elaSearch/', views.ela_store, name='ela_store'),
    path('theme/autocom/', views.autocom, name='autocom'),
]