from rest_framework import serializers


class CheckoutSubscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    price_id = serializers.CharField()


class CheckoutSessionSerializer(serializers.Serializer):
    currency = serializers.CharField()
    title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)