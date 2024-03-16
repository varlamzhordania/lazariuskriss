from rest_framework import serializers
from django.core.validators import MinValueValidator


class MatcherSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    level = serializers.IntegerField(required=True, validators=[MinValueValidator(0)])
    language = serializers.CharField(required=True, allow_blank=False)
    title = serializers.CharField(max_length=50, required=False, allow_blank=True)
    text = serializers.CharField(required=True, allow_blank=False)
