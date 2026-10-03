from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TouristLocation, UserFavorite

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email','first_name','last_name','role','is_active','is_verified','date_joined']
    list_filter = ['role','is_active','is_verified','is_blocked']
    search_fields = ['email','first_name','last_name','username']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Personal', {'fields': ('first_name','last_name','username','phone','profile_picture','bio','address','city','state')}),
        ('Role & Status', {'fields': ('role','is_active','is_staff','is_superuser','is_verified','is_blocked')}),
        ('Permissions', {'fields': ('groups','user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email','username','first_name','last_name','role','password1','password2')}),
    )

@admin.register(TouristLocation)
class TouristLocationAdmin(admin.ModelAdmin):
    list_display = ['name','state','is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(UserFavorite)

from .models import PasswordResetToken

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'is_used']
    list_filter  = ['is_used']
    readonly_fields = ['token', 'created_at']
