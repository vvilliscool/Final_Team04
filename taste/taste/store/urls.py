from django.urls import path, re_path

from . import views


app_name = 'store'

# urlpatterns = [
#     path('map/', views.taste_map, name='taste_map'),
#     path('theme/', views.theme, name='theme'),
# ]
urlpatterns = [
    path('map/', views.taste_map, name='taste_map'),
    path('map/pos/', views.geo_add, name='geo_add'),
    path('theme/', views.theme, name='theme'),
    path('elaSearch/', views.ela_store, name='ela_store'),
    path('theme/autocom/', views.autocom, name='autocom'),
    path('elaSearch/autocom/', views.autocom2, name='autocom2'),
    re_path(r'^(?P<store_pk>\d+)/$', views.store_detail, name='store_detail'),
]