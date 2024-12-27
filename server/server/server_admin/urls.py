from django.urls import path
from . import views

app_name = "server"  
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('return/', views.return_message, name='return'),
    path('send/', views.get_message, name='send'),
    path('user/', views.user, name='user'),
    path('pub_key', views.get_public_key, name='pub_key'),
    ]