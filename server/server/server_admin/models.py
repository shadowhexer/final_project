# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class Message(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    author = models.ForeignKey('server_admin.CustomUser', to_field='id', on_delete=models.CASCADE, related_name='messages') # Convert to integer field with foreign key on final version
    key = models.TextField()
    iv = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'message'
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):

    id = models.AutoField(primary_key=True)
    username = models.TextField(unique=True)
    email = models.TextField()
    password = models.TextField()
    public_key = models.TextField()

    class Meta:
        managed = False
        db_table = 'user'
    
    def __str__(self):
        return self.name