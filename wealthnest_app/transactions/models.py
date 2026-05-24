from django.db import models


class Transaction(models.Model):
    TYPES = [
        ('reward', 'Reward'),
        ('allowance', 'Allowance'),
        ('expense', 'Expense'),
        ('adjustment', 'Adjustment'),
        ('savings', 'Savings'),
    ]
    transaction_id = models.AutoField(primary_key=True)
    dependent = models.ForeignKey('dependents.FamilyDependent', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=15, choices=TYPES)
    amount = models.FloatField()
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    reference_chore = models.ForeignKey('chores.Chore', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} - {self.dependent.full_name}"

    @property
    def type_color(self):
        return {
            'reward': '#F6C90E',
            'allowance': '#10B981',
            'expense': '#FF6B6B',
            'adjustment': '#1E1B4B',
            'savings': '#8B5CF6',
        }.get(self.transaction_type, '#6B7280')

    @property
    def is_credit(self):
        return self.transaction_type in ['reward', 'allowance', 'adjustment']


class AllowanceSchedule(models.Model):
    FREQUENCIES = [('weekly', 'Weekly'), ('monthly', 'Monthly')]
    schedule_id = models.AutoField(primary_key=True)
    dependent = models.OneToOneField('dependents.FamilyDependent', on_delete=models.CASCADE)
    amount = models.FloatField()
    frequency = models.CharField(max_length=10, choices=FREQUENCIES, default='weekly')
    day_of_week = models.IntegerField(null=True, blank=True)
    day_of_month = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_credited = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'allowance_schedule'

    def __str__(self):
        return f"Allowance {self.frequency} ₹{self.amount} - {self.dependent.full_name}"
