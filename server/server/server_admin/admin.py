# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Message

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')  # Ensure 'is_active' is a valid field
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('id', 'author_id', 'message', 'timeStamp')  # Customize the fields to display
    search_fields = ('author_id', 'message')          # Add searchable fields
    list_filter = ('timeStamp',)                            # Add filter options

admin.site.register(CustomUser, CustomUserAdmin)