# payments/views.py

import stripe
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt # Only for simplicity in this example
from django.db import transaction

from django.conf import settings # new
from django.http.response import JsonResponse # new
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView
import json

from apps.accounts.models import Tier, User, UserSettings


logger = logging.getLogger(__name__)
# Initialize Stripe with your secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Replace this with your actual Price ID from the Stripe Dashboard
HEALTH_HERO_PRICE_ID = 'price_1RUnxqFRa8uCnmTD91rvnTpe' # <<< IMPORTANT: Update this!

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'payments/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'payments/cancelled/',
                payment_method_types=['card'],
                mode='subscription',
                client_reference_id=request.user.id,  # <-- Add this line!
                line_items=[
                    {
                        'price': HEALTH_HERO_PRICE_ID,
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

def payment_success_view(request):
    session_id = request.GET.get('session_id')
    session = None
    customer_email = None
    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            customer_email = session.get('customer_details', {}).get('email')
        except Exception as e:
            session = None

    return render(request, 'payments/success.html', {
        'session_id': session_id,
        'customer_email': customer_email,
    })

def payment_cancel_view(request):
    # Handle payment cancellation
    return render(request, 'payments/cancel.html')

def product_landing_page_view(request):
    # A simple page to initiate the payment
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'health_hero_price_id': HEALTH_HERO_PRICE_ID
    }
    return render(request, 'payments/product_page.html', context)

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook view to handle checkout session completion.
    """
    print("Stripe webhook called")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print(f"Stripe event constructed: {event['type']}")
    except ValueError:
        logger.warning("Stripe webhook received an invalid payload.")
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook received an invalid signature.")
        print("Invalid signature")
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Handling checkout.session.completed event")
        session = event['data']['object']
        print(f"Session object: {session}")
        user_id = session.get('client_reference_id')
        print(f"client_reference_id: {user_id}")
        if user_id is None:
            logger.error(f"client_reference_id not found in session {session.get('id')}. Cannot process order.")
            print(f"client_reference_id not found in session {session.get('id')}. Cannot process order.")
            return HttpResponse(status=200)

        try:
            with transaction.atomic():
                print(f"Looking up user with id: {user_id}")
                user = User.objects.get(id=user_id)
                print(f"User found: {user}")
                usersettings = user.usersettings
                print(f"UserSettings found: {usersettings}")

                # Idempotency check
                if usersettings.subscription_status == 'premium':
                    logger.info(f"User {user_id} is already a premium member. Webhook for session {session.get('id')} already processed.")
                    print(f"User {user_id} is already a premium member. Webhook for session {session.get('id')} already processed.")
                    return HttpResponse(status=200)

                premium_tier = Tier.objects.get(name__iexact='Premium')
                print(f"Premium tier found: {premium_tier}")
                usersettings.account_tier = premium_tier
                usersettings.subscription_status = 'premium'
                usersettings.payment_customer_id = session.get('customer')
                usersettings.payment_subscription_id = session.get('subscription')
                usersettings.save()
                print(f"UserSettings updated and saved for user {user.email} (ID: {user.id})")

                logger.info(f"Successfully upgraded user {user.email} (ID: {user.id}) to premium.")

        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist. Cannot upgrade.")
            print(f"User with ID {user_id} does not exist. Cannot upgrade.")
        except UserSettings.DoesNotExist:
            logger.error(f"UserSettings for user with ID {user_id} do not exist.")
            print(f"UserSettings for user with ID {user_id} do not exist.")
        except Tier.DoesNotExist:
            logger.error("Premium tier does not exist in the database.")
            print("Premium tier does not exist in the database.")
        except Exception as e:
            logger.error(f"Unexpected error processing webhook for user {user_id}: {e}")
            print(f"Unexpected error processing webhook for user {user_id}: {e}")

    else:
        print(f"Unhandled event type: {event['type']}")

    return HttpResponse(status=200)