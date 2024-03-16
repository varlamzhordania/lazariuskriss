from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import count_and_check_payment
from .serializers import MatcherSerializer


class MatcherView(APIView):
    """
    API endpoint for matching.

    Permissions:
    - AllowAny: Allows unrestricted access to this endpoint.

    Methods:
    - post: Processes a POST request containing data for matching.

    Fields (from MatcherSerializer):
    - username (optional): The username associated with the text (default: None).
    - level (required): The level of the user, must be an integer greater than or equal to 0.
    - language (required): The language associated with the text, cannot be blank.
    - title (optional): The title associated with the text, maximum length of 50 characters (default: None).
    - text (required): The text associated with the text, cannot be blank.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        """
        Process a POST request containing data for matching.

        Parameters:
        - request: HTTP request object
        - format: Optional format for response data (default: None)

        Returns:
        - Response: HTTP response containing the result of celery task.
        """
        # Deserialize request data
        serializer = MatcherSerializer(data=request.data)

        if serializer.is_valid():
            # Extract validated data from serializer
            username = serializer.validated_data.get("username", None)
            level = serializer.validated_data.get("level", None)
            language = serializer.validated_data.get("language", None)
            title = serializer.validated_data.get("title", None)
            text = serializer.validated_data.get("text", None)

            # Asynchronously process text using Celery task
            response = count_and_check_payment.delay(username, language, title, text, level)

            # Wait for the task to complete and retrieve the result
            data = response.get()

            # Return the processed data as HTTP response
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Return validation errors if serializer is invalid
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
