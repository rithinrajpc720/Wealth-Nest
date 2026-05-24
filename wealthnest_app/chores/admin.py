from django.contrib import admin
from .models import Chore, ChoreCategory, ChoreSubmission


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('chore_name', 'family', 'assigned_to', 'reward_amount', 'difficulty', 'status', 'deadline')
    list_filter = ('status', 'difficulty')


admin.site.register(ChoreCategory)
admin.site.register(ChoreSubmission)
