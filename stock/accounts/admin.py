from django.contrib import admin
from .models import Profile, Vendor, SalesTeam


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for the Profile model."""
    list_display = ('user', 'telephone', 'email', 'role', 'status')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """Admin interface for the Vendor model."""
    fields = ('name', 'phone_number', 'address')
    list_display = ('name', 'phone_number', 'address')
    search_fields = ('name', 'phone_number', 'address')


@admin.register(SalesTeam)
class SalesTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'zone', 'sales_goal', 'achievement_rate')
