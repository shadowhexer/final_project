from django.urls import path
from . import views

app_name = "admin"  
urlpatterns = [
    path('register/', views.register, name='register'),
    path('send/', views.send, name='send'),
    path('receive/', views.get, name='get')
    ]