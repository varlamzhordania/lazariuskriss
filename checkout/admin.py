from django.contrib import admin
from .models import Transaction, Subscription


# Register your models here.

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'user_email', 'stripe_customer_id', 'stripe_subscription_id', 'paid_amount', 'active', 'start_date',
        'end_date',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'amount', 'status', 'gateway', 'create_at', 'update_at',)


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
