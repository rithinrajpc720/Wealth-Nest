"""Achievement triggers."""
from django.db.models import Sum
from .models import Achievement, UserAchievement


def check_achievements(dependent):
    """Check & award achievements for the dependent based on their stats.
    Returns list of newly earned Achievement objects."""
    from chores.models import Chore
    from goals.models import SavingsGoal
    from transactions.models import Transaction

    earned_ids = set(UserAchievement.objects.filter(dependent=dependent).values_list('achievement_id', flat=True))
    newly_earned = []

    chores_count = Chore.objects.filter(assigned_to=dependent, status='approved').count()
    goals_done = SavingsGoal.objects.filter(dependent=dependent, is_completed=True).count()
    savings_total = SavingsGoal.objects.filter(dependent=dependent).aggregate(s=Sum('current_amount'))['s'] or 0
    streak = dependent.streak_days
    xp = dependent.xp_points

    for ach in Achievement.objects.all():
        if ach.achievement_id in earned_ids:
            continue
        triggered = False
        if ach.trigger_type == 'first_chore' and chores_count >= 1:
            triggered = True
        elif ach.trigger_type == 'chores_completed' and chores_count >= ach.trigger_value:
            triggered = True
        elif ach.trigger_type == 'streak_days' and streak >= ach.trigger_value:
            triggered = True
        elif ach.trigger_type == 'savings_amount' and savings_total >= ach.trigger_value:
            triggered = True
        elif ach.trigger_type == 'goals_reached' and goals_done >= ach.trigger_value:
            triggered = True
        elif ach.trigger_type == 'first_goal' and goals_done >= 1:
            triggered = True
        elif ach.trigger_type == 'xp_points' and xp >= ach.trigger_value:
            triggered = True

        if triggered:
            UserAchievement.objects.create(dependent=dependent, achievement=ach)
            dependent.xp_points += ach.xp_reward
            dependent.save(update_fields=['xp_points'])
            newly_earned.append(ach)

    return newly_earned
