from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Subscription(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_("User"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='user_subscriptions'
    )
    user_email = models.EmailField(verbose_name=_("Email"), blank=True, null=True, max_length=254)
    stripe_subscription_id = models.CharField(
        max_length=100,
        verbose_name=_("Subscription ID"),
        blank=True,
        null=True,
        unique=True
    )
    stripe_customer_id = models.CharField(
        max_length=100,
        verbose_name=_("Customer ID"),
        blank=True,
        null=True,
    )
    stripe_price_id = models.CharField(
        max_length=100,
        verbose_name=_("Price ID"),
        blank=True,
        null=True,
    )
    paid_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("Paid Amount"),
        help_text=_("format : maximum amount 99999.99"),
        error_messages={
            "name": {
                "max_length": _("the amount must be between 0 and 99999.99"),
            },
        },
    )
    active = models.BooleanField(default=True, verbose_name=_("Activate"))
    start_date = models.DateTimeField(verbose_name=_("Start Date"), blank=True, null=True)
    end_date = models.DateTimeField(verbose_name=_("End Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.id} - {self.user_email} - {self.stripe_subscription_id}"


class Transaction(models.Model):
    class StatusPaymentChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _("Cancelled")

    user = models.ForeignKey(
        get_user_model(), blank=True, unique=False, null=True,
        related_name="user_transactions",
        verbose_name=_("User"),
        on_delete=models.CASCADE
    )
    payment_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        unique=False,
        null=True,
        blank=True,
        verbose_name=_("amount have to pay"),
        help_text=_("format : maximum amount 99999.99"),
        error_messages={
            "name": {
                "max_length": _("the amount must be between 0 and 99999.99"),
            },
        },
    )
    status = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("payment status"),
        choices=StatusPaymentChoices, default=StatusPaymentChoices.PENDING,
    )

    gateway = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_("payment method"),
        help_text=_("format : credit,debit,mastercard,paypal...etc")
    )

    create_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("date payment created"),
        help_text=_("format : y-m-d H:M:S")
    )
    update_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("date payment last updated"),
        help_text=_("format : y-m-d H:M:S")
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ["-create_at"]

    def __str__(self):
        return f"{self.id} - {self.user} : {self.payment_id}"
