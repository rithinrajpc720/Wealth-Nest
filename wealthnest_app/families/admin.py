from django.contrib import admin
from .models import Family


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_name', 'join_pin', 'is_active', 'created_at')
