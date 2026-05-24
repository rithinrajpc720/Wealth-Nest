from django.db import models
from accounts.models import Login
from families.models import Family


class HouseholdHead(models.Model):
    head_id = models.AutoField(primary_key=True)
    login = models.OneToOneField(Login, on_delete=models.CASCADE)
    family = models.OneToOneField(Family, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    family_size = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'household_head'

    def __str__(self):
        return self.full_name
