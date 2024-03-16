from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import count_and_check_payment, process_text
from .serializers import MatcherSerializer

from decimal import Decimal, ROUND_HALF_UP


class MatcherView(APIView):
    """
    API endpoint for matching and processing text.

    Permissions:
    - AllowAny: Allows unrestricted access to this endpoint.

    Methods:
    - post: Processes a POST request containing data for matching and processing.

    Fields (from MatcherSerializer):
    - username (optional): The username associated with the text (default: None).
    - level (required): The level of the user, must be an integer greater than or equal to 0.
    - language (required): The language associated with the text, cannot be blank.
    - title (optional): The title associated with the text, maximum length of 50 characters (default: None).
    - text (required): The text to be processed, cannot be blank.
    """
    permission_classes = [permissions.AllowAny]
    per_sentence = Decimal('0.05')  # Price per sentence

    def post(self, request, format=None):
        """
        Process a POST request containing data for matching and processing.

        Parameters:
        - request: HTTP request object
        - format: Optional format for response data (default: None)

        Returns:
        - Response: HTTP response containing the result of processing.
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

            # Handle different processing results
            if data["status"] == "payment_required":
                # Calculate payment amount and format it to 4 decimal places
                pay_amount = (Decimal(data["sentence_count"]) * self.per_sentence).quantize(
                    Decimal("0.0001"),
                    rounding=ROUND_HALF_UP
                    )

                result = {
                    "message": f"Your text is too long, you need to pay ${pay_amount} to continue with the process",
                    "amount": pay_amount,
                    "status": "payment_required",
                }
            elif data["status"] == "no_payment_required":
                # Asynchronously process text
                processed_object = process_text.delay()
                processed_data = processed_object.get()

                result = {
                    "message": processed_data["message"],
                    "status": "no_payment_required",
                    "data": "Your data"
                }
            else:
                return Response(
                    {"message": "The returned result is invalid"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Return the processed data as HTTP response
            return Response(result, status=status.HTTP_200_OK)
        else:
            # Return validation errors if serializer is invalid
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
