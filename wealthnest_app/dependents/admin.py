from django.contrib import admin
from .models import FamilyDependent


@admin.register(FamilyDependent)
class FamilyDependentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'family', 'dependent_type', 'wallet_balance', 'xp_points', 'streak_days')
    list_filter = ('dependent_type',)
