from django.db import models


class SavingsGoal(models.Model):
    goal_id = models.AutoField(primary_key=True)
    dependent = models.ForeignKey('dependents.FamilyDependent', on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=200)
    target_amount = models.FloatField()
    current_amount = models.FloatField(default=0.0)
    target_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=10, default='🎯')
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'savings_goal'
        ordering = ['-created_at']

    def __str__(self):
        return self.goal_name

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, round((self.current_amount / self.target_amount) * 100, 1))

    @property
    def remaining_amount(self):
        return max(0, self.target_amount - self.current_amount)


class GoalContribution(models.Model):
    contribution_id = models.AutoField(primary_key=True)
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_contribution'
        ordering = ['-created_at']

    def __str__(self):
        return f"₹{self.amount} -> {self.goal.goal_name}"
