from django.urls import path, re_path

from . import views


app_name = 'review'

urlpatterns = [
    # review
    path('', views.review_list, name='review_list'),
    path('create/', views.review_create, name='review_create'),
    re_path(r'^(?P<review_pk>\d+)/$', views.review_detail, name='review_detail'),
    re_path(r'^(?P<review_pk>\d+)/like-toggle/$', views.review_like_toggle, name='review_like_toggle'),

    # comment
    re_path(r'^(?P<review_pk>\d+)/comment/create/$', views.comment_create, name='comment_create'),
]