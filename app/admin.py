import typing_extensions
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import *



admin.site.register(sqlserverconn)
admin.site.register(IssueItem)
admin.site.register(GroupedItems)
admin.site.register(Custom_UOM)
admin.site.register(Person)
admin.site.register(Labour)




from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Define fields to display in the list view of the admin interface
    list_display = ('username', 'email', 'tenant', 'is_staff', 'is_superuser')
    
    # Define fields to filter by in the admin interface
    list_filter = ('tenant', 'is_staff', 'is_superuser')

    # Define fields to search by in the admin interface
    search_fields = ('username', 'email')

    # Define fields to include in the detail view of the admin interface
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'tenant')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Optionally, define additional actions to perform on selected users
    actions = ['make_staff', 'make_superuser']

    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)

    def make_superuser(self, request, queryset):
        queryset.update(is_staff=True, is_superuser=True)

class TenantAdmin(admin.ModelAdmin):
    pass  # You can customize this further if needed

# Register models with their admin classes
admin.site.register(CustomUser, CustomUserAdmin)

