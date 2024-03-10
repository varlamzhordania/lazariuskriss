import json
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CheckoutSessionSerializer, CheckoutSubscriptionSerializer
from .models import Transaction, Subscription
from django.contrib.auth import get_user_model
from django.conf import settings
import stripe
from decimal import Decimal
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutSessionView(APIView):
    """
    API endpoint for creating a Stripe Checkout session.

    This view allows clients to initiate a payment session by providing
    necessary details such as currency, title, and amount.

    Parameters:
    - currency: The currency code (default: 'usd').
    - title: The title or name of the product.
    - amount: The amount to be charged in the specified currency.

    Returns:
    - url: The Stripe Checkout session URL.

    Example Usage:
    POST /api/checkout/session/
    {
        "currency": "usd",
        "title": "Product Name",
        "amount": 10.99
    }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Create a new Stripe Checkout session.

        This method validates the input parameters and creates a new
        Checkout session using the Stripe API.

        Args:
        - currency (str): The currency code.
        - title (str): The title or name of the product.
        - amount (Decimal): The amount to be charged.

        Returns:
        - Response: JSON response containing the Checkout session URL.

        Raises:
        - Response: JSON response with an error message if any exception occurs.
        """
        serializer = CheckoutSessionSerializer(data=request.data)

        if serializer.is_valid():
            currency = serializer.validated_data.get('currency', 'usd')
            title = serializer.validated_data.get('title')
            amount = serializer.validated_data.get('amount')

            try:
                # Create a new Checkout session using the Stripe API
                session = stripe.checkout.Session.create(
                    mode="payment",
                    success_url=f"{settings.FRONTEND_URL}/?payment=success",
                    cancel_url=f"{settings.FRONTEND_URL}/?payment=cancel",
                    line_items=[
                        {
                            "price_data": {
                                "currency": currency,
                                "product_data": {
                                    "name": title,
                                },
                                "unit_amount": int(amount * 100),
                            },
                            "quantity": 1,
                        }
                    ],
                )
                Transaction.objects.create(
                    currency=currency,
                    amount=amount,
                    gateway="stripe",
                    payment_id=session.id
                )

                # Return the Checkout session URL to the client
                return Response({"url": session.url})
            except ValueError as ve:
                return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as se:
                return Response({"error": str(se)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutSubscriptionView(APIView):
    """
    API endpoint for creating a Stripe Checkout subscription session.

    This view allows clients to initiate a subscription session by providing
    necessary details such as email and price ID.

    Parameters:
    - email: The customer's email address.
    - price_id: The ID of the Stripe Price object representing the subscription.

    Returns:
    - url: The Stripe Checkout subscription session URL.

    Example Usage:
    POST /api/checkout/subscribe/
    {
        "email": "customer@example.com",
        "price_id": "price_12345"
    }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Create a new Stripe Checkout subscription session.

        This method validates the input parameters and creates a new
        subscription session using the Stripe API.

        Args:
        - email (str): The customer's email address.
        - price_id (str): The ID of the Stripe Price object representing the subscription.

        Returns:
        - Response: JSON response containing the Checkout subscription session URL.

        Raises:
        - Response: JSON response with an error message if any exception occurs.
        """
        serializer = CheckoutSubscriptionSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            price_id = serializer.validated_data.get('price_id')

            try:
                # Create a new Checkout subscription session using the Stripe API
                session = stripe.checkout.Session.create(
                    mode="subscription",
                    success_url=f"{settings.FRONTEND_URL}/?payment=success",
                    cancel_url=f"{settings.FRONTEND_URL}/?payment=cancel",
                    line_items=[{"price": price_id, "quantity": 1}],
                    customer_email=email,
                    payment_method_collection="always",
                )
                Transaction.objects.create(
                    gateway="stripe",
                    payment_id=session.id
                )

                # Return the Checkout subscription session URL to the client
                return Response({"url": session.url})
            except stripe.error.StripeError as se:
                return Response({"error": str(se)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutCancelSubscriptionView(APIView):
    """
    API endpoint for canceling a Stripe subscription.

    This view allows clients to cancel a subscription identified by the provided `subscription_id`.

    Permissions:
    - AllowAny: Accessible by anyone, as it's intended for subscription cancellation.

    Methods:
    - post: Handles the cancellation of a Stripe subscription.

    Request Payload:
    - subscription_id (str): The ID of the subscription to be canceled.

    Returns:
    - Response: JSON response indicating the success or failure of the subscription cancellation.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Cancel a Stripe subscription.

        This method cancels a subscription identified by the provided `subscription_id`.

        Args:
        - request (Request): Django REST framework request object containing the subscription ID.

        Returns:
        - Response: JSON response indicating the success or failure of the subscription cancellation.
        """

        data = request.data
        subscription_id = data.get("subscription_id")

        if not subscription_id:
            return Response({"error": "subscription_id field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the subscription from the database
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)

            # Cancel the subscription using the Stripe API
            stripe.Subscription.cancel(subscription.stripe_subscription_id)

            # Optionally, mark the subscription as inactive in the database or let webhook handle it
            subscription.active = False
            subscription.save()

            return Response({"message": "Subscription canceled successfully."}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as se:
            return Response({"error": str(se)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Subscription.DoesNotExist:
            return Response({"error": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebhookView(APIView):
    """
    Webhook endpoint for handling Stripe events.

    This view is responsible for processing Stripe webhook events,
    such as 'checkout.session.completed' and 'invoice.paid'.

    Permissions:
    - AllowAny: Accessible by anyone, as it's intended for Stripe to send webhook events.

    Methods:
    - post: Handles incoming Stripe webhook events and updates the database accordingly.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle incoming Stripe webhook events.

        This method processes Stripe webhook events and updates the database based on the event type.

        Args:
        - request (Request): Django REST framework request object containing the webhook payload.

        Returns:
        - Response: HTTP response indicating the success or failure of processing the webhook event.
        """

        payload = request.data
        event = None

        try:
            # Construct a Stripe Event object from the payload
            event = stripe.Event.construct_from(payload, stripe.api_key)
        except ValueError as e:
            # Return a 400 Bad Request response if the payload cannot be parsed
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event.type == 'checkout.session.completed':
            # Handle 'checkout.session.completed' event
            data = event.data.object
            transaction = Transaction.objects.get(payment_id=data['id'])
            transaction.status = Transaction.StatusPaymentChoices.COMPLETED
            if not transaction.amount:
                transaction.amount = data['amount_total'] / 100
            transaction.save()
        elif event.type == 'invoice.paid':
            # Handle 'invoice.paid' event
            data = event.data.object
            customer_email = data.customer_email
            customer_id = data.customer
            subscription_id = data['subscription']
            price_id = data.lines.data[0].price.id
            paid_amount = data.amount_paid
            start_date = timezone.datetime.utcfromtimestamp(data.lines.data[0].period.start)
            end_date = timezone.datetime.utcfromtimestamp(data.lines.data[0].period.end)

            # Update or create a Subscription record in the database
            Subscription.objects.update_or_create(
                user_email=customer_email,
                stripe_subscription_id=subscription_id,
                defaults={
                    "active": True,
                    "start_date": start_date,
                    "end_date": end_date,
                    "stripe_customer_id": customer_id,
                    "stripe_price_id": price_id,
                    "paid_amount": paid_amount / 100,
                }
            )
        elif event.type == 'customer.subscription.deleted':
            data = event.data.object
            subscription_id = data["id"]

            try:
                # Attempt to get the subscription from the database
                subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)

                # Mark the subscription as inactive
                subscription.active = False
                subscription.save()

            except Subscription.DoesNotExist:
                # Handle the case where the subscription is not found
                print(f"Subscription with ID {subscription_id} not found in the database.")
            except Exception as e:
                # Handle other exceptions that might occur during the process
                print(f"An error occurred: {str(e)}")

        # Return a 200 OK response upon successful processing of the webhook event
        return Response(status=status.HTTP_200_OK)
