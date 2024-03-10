from django.urls import path
from .views import CheckoutSessionView, CheckoutSubscriptionView, WebhookView,CheckoutCancelSubscriptionView

app_name = 'checkout'

urlpatterns = [
    path('checkout/session/', CheckoutSessionView.as_view(), name='checkoutSession'),
    path('checkout/subscribe/', CheckoutSubscriptionView.as_view(), name='checkoutSubscription'),
    path('checkout/subscribe/cancel/', CheckoutCancelSubscriptionView.as_view(), name='checkoutCancelSubscription'),
    path('checkout/webhook/', WebhookView.as_view(), name='webhook')

]
