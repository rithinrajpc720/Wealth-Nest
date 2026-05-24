from django.contrib import admin
from .models import ExpenseCategory, ChoreCategoryAdmin, GoalCategory

admin.site.register(ExpenseCategory)
admin.site.register(ChoreCategoryAdmin)
admin.site.register(GoalCategory)
