from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Administration configuration for custom User model."""

    list_display = ("email", "full_name", "is_staff", "is_active", "user_roles")
    search_fields = ("email", "full_name")
    list_filter = ("is_staff", "is_active", "user_roles")
