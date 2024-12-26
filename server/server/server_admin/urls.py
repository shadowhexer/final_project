from django.urls import path
from . import views

app_name = "server"  
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('send/', views.send, name='send'),
    path('receive/', views.get, name='get'),
    path('user/', views.user, name='user'),
    ]