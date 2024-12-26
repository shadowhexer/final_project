# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

# Create a custom user model
# https://learndjango.com/tutorials/django-custom-user-model
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create a custom user model based on user type
class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser."""

    # Create a new user with the given email and password.
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Create a new superuser with the given email and password.
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Validation for consistency
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(username, email, password, **extra_fields)


# Message model
class Message(models.Model):

    id = models.AutoField(primary_key=True)
    message = models.TextField()
    # Convert to integer field with foreign key on final version
    author_id = models.ForeignKey('server_admin.CustomUser', to_field='id', on_delete=models.CASCADE, related_name='messages', db_column='author_id') 
    key = models.TextField()
    iv = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False # Set to False to prevent Django from creating a table for this model
        db_table = 'message'
    
    def __str__(self):
        return self.name


# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):

    id = models.AutoField(primary_key=True)
    username = models.TextField(unique=True)
    email = models.TextField()
    password = models.TextField()
    public_key = models.TextField()
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    # Custom user manager
    objects = CustomUserManager()

    class Meta:
        managed = False
        db_table = 'user'
    
    def __str__(self):
        return self.name