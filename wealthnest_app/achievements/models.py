from django.db import models


class Achievement(models.Model):
    BADGE_TYPES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    TRIGGER_TYPES = [
        ('chores_completed', 'Chores Completed'),
        ('streak_days', 'Streak Days'),
        ('savings_amount', 'Savings Amount'),
        ('goals_reached', 'Goals Reached'),
        ('first_chore', 'First Chore'),
        ('first_goal', 'First Goal'),
        ('xp_points', 'XP Points'),
    ]

    achievement_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default='🏆')
    xp_reward = models.IntegerField(default=0)
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='bronze')
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_value = models.IntegerField(default=1)
    hint = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'achievement'
        ordering = ['trigger_value']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user_achievement_id = models.AutoField(primary_key=True)
    dependent = models.ForeignKey('dependents.FamilyDependent', on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_achievement'
        unique_together = ('dependent', 'achievement')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.dependent.full_name} - {self.achievement.name}"
