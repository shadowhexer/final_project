from django.urls import path
from . import views

app_name = "client"
urlpatterns = [
    path('sent/', views.send_message, name='send_message'),
    path('message/', views.receive_message, name='receive_message')
    ]