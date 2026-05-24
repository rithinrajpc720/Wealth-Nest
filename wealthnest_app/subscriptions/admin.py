from django.contrib import admin
from .models import Plan, Subscription, Payment


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price_monthly', 'price_yearly', 'is_popular')
    list_filter = ('is_popular',)


@admin.register(Subscription)
class SubAdmin(admin.ModelAdmin):
    list_display = ('family', 'plan', 'status', 'billing_cycle', 'expires_at')
    list_filter = ('status', 'plan')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'subscription', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('invoice_number', 'transaction_id')
