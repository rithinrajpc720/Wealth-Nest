from django.contrib import admin
from .models import Transaction, AllowanceSchedule


@admin.register(Transaction)
class TxAdmin(admin.ModelAdmin):
    list_display = ('dependent', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type',)


admin.site.register(AllowanceSchedule)
