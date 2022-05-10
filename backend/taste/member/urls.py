from django.urls import path, re_path

from . import views

app_name = 'member'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('ranking/', views.ranking, name='ranking'),
    path('mypage/', views.mypage, name='mypage'),
    path('agg_user_func/', views.agg_user_func, name='agg_user_func'),
    path('modify/', views.modify, name='modify'),
    path('change_password/',views.change_password, name='change_password'),
    path('user_delete/', views.user_delete, name='user_delete'),
]