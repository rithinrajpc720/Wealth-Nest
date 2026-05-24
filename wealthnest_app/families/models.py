from django.db import models
import random


class Family(models.Model):
    family_id = models.AutoField(primary_key=True)
    family_name = models.CharField(max_length=100)
    join_pin = models.CharField(max_length=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'family'

    def __str__(self):
        return self.family_name

    @staticmethod
    def generate_pin():
        return str(random.randint(1000, 9999))

    @property
    def member_count(self):
        return self.familydependent_set.count() + 1  # + head
