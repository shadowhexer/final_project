from django.urls import path
from . import views

app_name = "admin"  
urlpatterns = [
    path('send/', views.send, name='send'),
    path('receive/', views.get, name='get')
    ]