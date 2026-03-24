from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для пользователей"""
    list_display = ('id', 'email', 'phone', 'country', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'country')
    search_fields = ('email', 'phone', 'country')
    ordering = ('email',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'password')
        }),
        ('Персональная информация', {
            'fields': ('avatar', 'phone', 'country')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone', 'country', 'avatar', 'is_staff', 'is_active'),
        }),
    )