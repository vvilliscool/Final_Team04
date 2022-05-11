"""taste URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from review import views as rviews
from store import views as sviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sviews.theme, name='index'),
    # path('', views.index, name='index'),
    
    path('ranking/', views.ranking, name='ranking'),
    path('map/', views.map, name='map'),
    path('mypage/', views.mypage, name='mypage'),

    # review App
    path('review/', include('review.urls', namespace='review')),

    # member App
    path('member/', include('member.urls', namespace='member')),

    # store App
    path('store/', include('store.urls', namespace='store')),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
