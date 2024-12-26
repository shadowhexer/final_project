from django.urls import path
from . import views

app_name = "client"
urlpatterns = [
    path('register/', views.registration, name='registration'),
    # path('login/', views.login, name='login'),
    path('send/', views.send_message, name='send_message'),
    path('message/', views.receive_message, name='receive_message'),
    path('user', views.get_user, name='get_user'),
    ]