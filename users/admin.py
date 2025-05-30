from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar', 'website')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar', 'website')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
