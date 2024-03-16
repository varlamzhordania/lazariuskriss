import json

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MatcherSerializer
from .tasks import count_and_check_payment


# Create your views here.


class MatcherView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = MatcherSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data.get("username", None)
            level = serializer.validated_data.get("level", None)
            language = serializer.validated_data.get("language", None)
            title = serializer.validated_data.get("title", None)
            text = serializer.validated_data.get("text", None)

            response = count_and_check_payment.delay(username, language, title, text, level)

            data = response.get()

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
