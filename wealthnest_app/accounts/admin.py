from django.contrib import admin
from .models import Login, PasswordResetOTP


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_suspended', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_suspended')
    search_fields = ('username', 'email')


admin.site.register(PasswordResetOTP)
admin.site.site_header = 'WealthNest Admin'
admin.site.site_title = 'WealthNest'
