# payments/views.py

import stripe
import os
from dotenv import load_dotenv

load_dotenv()
import logging
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt  # Only for simplicity
from django.db import transaction

from django.http.response import JsonResponse  # new
from django.views.decorators.csrf import csrf_exempt  # new
from django.views.generic.base import TemplateView

from apps.accounts.models import Tier, User, UserSettings


logger = logging.getLogger(__name__)
# Configure logger
logger = logging.getLogger("stripe.webhook")

# Initialize Stripe with secret key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

HEALTH_HERO_PRICE_ID = "price_1RUDo3FSaExQ9wThw9bW3ebR"  # <<< IMPORTANT: Update this!


@csrf_exempt
def create_checkout_session(request):
    if request.method == "GET":
        domain_url = "https://medminder-fhhw.onrender.com/"
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=f"{domain_url}payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain_url}payments/cancelled/",
                payment_method_types=["card"],
                mode="subscription",
                customer_email=request.user.email,
                metadata={
                    "user_id": request.user.id,  # Add metadata to track the user
                },
                line_items=[
                    {
                        "price": HEALTH_HERO_PRICE_ID,
                        "quantity": 1,
                    }
                ],
            )
            print(f"Created checkout session: {checkout_session.id}")
            return JsonResponse({"sessionId": checkout_session.id})
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Invalid request method"})


def payment_success_view(request):
    session_id = request.GET.get("session_id")
    session = None
    customer_email = None
    if session_id:
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            customer_email = session.get("customer_details", {}).get("email")
        except Exception as e:
            session = None

    return render(
        request,
        "payments/success.html",
        {
            "session_id": session_id,
            "customer_email": customer_email,
        },
    )


def payment_cancel_view(request):
    # Handle payment cancellation
    return render(request, "payments/cancel.html")


def product_landing_page_view(request):
    # A simple page to initiate the payment
    context = {
        "stripe_publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
        "health_hero_price_id": HEALTH_HERO_PRICE_ID,
    }
    return render(request, "payments/product_page.html", context)


@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": os.environ.get("STRIPE_PUBLISHABLE_KEY")}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def stripe_webhook(request):
    logger.info("⭐️ Webhook endpoint called")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not sig_header:
        logger.error("❌ No Stripe signature found in headers")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
        logger.info(f"✅ Event constructed successfully: {event['type']}")
    except ValueError as e:
        logger.error(f"❌ Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        logger.info("🎉 Processing checkout.session.completed event")
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        if not customer_email:
            logger.error("❌ No customer email found in session")
            return HttpResponse(status=200)
        logger.info(f"📧 Found customer email: {customer_email}")

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(email=customer_email)
                usersettings = UserSettings.objects.select_for_update().get(user=user)
                premium_tier, created = Tier.objects.get_or_create(
                    name="Premium",
                    defaults={
                        "description": "Premium subscription with all features",
                        "priority": 1,
                        "is_default": False,
                        "max_reminders": None,
                        "max_viewers": None,
                        "can_use_sms_reminders": True,
                    },
                )
                usersettings.account_tier = premium_tier
                usersettings.subscription_status = "premium"
                usersettings.payment_customer_id = session.get("customer")
                usersettings.payment_subscription_id = session.get("subscription")
                usersettings.save()
                logger.info("User settings saved successfully")
        except User.DoesNotExist:
            logger.error(f"❌ User with email {customer_email} not found")
            return HttpResponse(status=200)
        except UserSettings.DoesNotExist:
            logger.error(f"❌ UserSettings for user {customer_email} not found")
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"❌ Error updating user settings: {str(e)}", exc_info=True)
            return HttpResponse(status=500)

    return HttpResponse(status=200)
