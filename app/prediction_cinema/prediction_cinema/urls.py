"""
URL configuration for prediction_cinema project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from app_django import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(next_page='home'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(next_page='home'), name='logout'),
    path('inscription/', views.inscription, name='inscription'),
    path('predcition/', views.prediction, name='prediction'),
    path('historique/', views.historique, name='historique'),
]
