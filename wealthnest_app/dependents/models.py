from django.db import models
from accounts.models import Login
from families.models import Family
from datetime import date


class FamilyDependent(models.Model):
    DEP_TYPES = [
        ('child', 'Child'),
        ('teen', 'Teen'),
        ('young_adult', 'Young Adult'),
    ]
    dependent_id = models.AutoField(primary_key=True)
    login = models.OneToOneField(Login, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    dependent_type = models.CharField(max_length=15, choices=DEP_TYPES, default='child')
    wallet_balance = models.FloatField(default=0.0)
    xp_points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'family_dependent'

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    @property
    def avatar_initial(self):
        return self.full_name[0].upper() if self.full_name else '?'

    @property
    def level(self):
        return max(1, self.xp_points // 100 + 1)

    @property
    def xp_to_next_level(self):
        return (self.level * 100) - self.xp_points
