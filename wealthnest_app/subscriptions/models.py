from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)              # Free, Pro, Premium
    slug = models.SlugField(max_length=20, unique=True)  # free, pro, premium
    tagline = models.CharField(max_length=200, blank=True)
    price_monthly = models.FloatField(default=0)
    price_yearly = models.FloatField(default=0)
    max_dependents = models.IntegerField(default=2)
    max_chores = models.IntegerField(default=10)
    max_goals = models.IntegerField(default=3)
    has_ai = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=False)
    has_export = models.BooleanField(default=False)
    has_achievements = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#1E1B4B')
    icon = models.CharField(max_length=10, default='📦')
    is_popular = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    features = models.TextField(blank=True, help_text='One feature per line')

    class Meta:
        db_table = 'plan'
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    @property
    def yearly_savings(self):
        if self.price_monthly == 0:
            return 0
        return round((self.price_monthly * 12) - self.price_yearly)

    @property
    def yearly_savings_percent(self):
        if self.price_monthly == 0:
            return 0
        return round(((self.price_monthly * 12 - self.price_yearly) / (self.price_monthly * 12)) * 100)


class Subscription(models.Model):
    STATUSES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('trial', 'Trial'),
    ]
    CYCLES = [('monthly', 'Monthly'), ('yearly', 'Yearly')]

    subscription_id = models.AutoField(primary_key=True)
    family = models.OneToOneField('families.Family', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    billing_cycle = models.CharField(max_length=10, choices=CYCLES, default='monthly')
    status = models.CharField(max_length=15, choices=STATUSES, default='active')
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscription'

    def __str__(self):
        return f'{self.family.family_name} - {self.plan.name}'

    @property
    def is_active(self):
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    @property
    def days_remaining(self):
        if not self.expires_at:
            return 9999
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    def extend(self, cycle='monthly'):
        days = 30 if cycle == 'monthly' else 365
        base = self.expires_at if self.expires_at and self.expires_at > timezone.now() else timezone.now()
        self.expires_at = base + timedelta(days=days)
        self.billing_cycle = cycle
        self.status = 'active'
        self.save()


class Payment(models.Model):
    STATUSES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    ]
    METHODS = [
        ('card', 'Credit / Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]

    payment_id = models.AutoField(primary_key=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    billing_cycle = models.CharField(max_length=10, default='monthly')
    amount = models.FloatField()
    currency = models.CharField(max_length=5, default='INR')
    payment_method = models.CharField(max_length=15, choices=METHODS, default='card')
    status = models.CharField(max_length=10, choices=STATUSES, default='success')
    transaction_id = models.CharField(max_length=50, unique=True)
    invoice_number = models.CharField(max_length=30, unique=True)
    payer_name = models.CharField(max_length=100, blank=True)
    last_four = models.CharField(max_length=4, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.invoice_number} - ₹{self.amount}'

    @staticmethod
    def generate_transaction_id():
        return 'WN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))

    @staticmethod
    def generate_invoice_number():
        from datetime import datetime
        return 'INV-' + datetime.now().strftime('%Y%m') + '-' + ''.join(random.choices(string.digits, k=6))
