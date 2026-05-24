from django.db import models


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, default='💰')
    color = models.CharField(max_length=7, default='#1E1B4B')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expense_category'
        verbose_name_plural = 'Expense Categories'

    def __str__(self):
        return self.name


class ChoreCategoryAdmin(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, default='🧹')
    color = models.CharField(max_length=7, default='#10B981')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chore_category_admin'
        verbose_name_plural = 'Chore Categories (Admin)'

    def __str__(self):
        return self.name


class GoalCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, default='🎯')
    color = models.CharField(max_length=7, default='#F6C90E')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_category'
        verbose_name_plural = 'Goal Categories'

    def __str__(self):
        return self.name
