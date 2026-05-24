from django.db import models
from django.utils import timezone
import hashlib
import random


class Login(models.Model):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('head', 'Household Head'),
        ('dependent', 'Family Dependent'),
    ]
    LOGIN_ID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    user_password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=15, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    user_phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login'

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    def set_password(self, raw):
        self.user_password = hashlib.sha256(raw.encode()).hexdigest()

    def check_password(self, raw):
        return self.user_password == hashlib.sha256(raw.encode()).hexdigest()


class PasswordResetOTP(models.Model):
    otp_id = models.AutoField(primary_key=True)
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'password_reset_otp'

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
