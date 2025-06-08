# payments/views.py

import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt # Only for simplicity in this example

from django.conf import settings # new
from django.http.response import JsonResponse # new
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView
import json

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
                mode='subscription',  # <-- Use 'subscription' for recurring payments
                line_items=[
                    {
                        'price': HEALTH_HERO_PRICE_ID,  # <-- Use your Stripe Price ID here
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
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        email = session.get('customer_details', {}).get('email')

        from django.contrib.auth import get_user_model
        from apps.accounts.models import Tier, UserSettings
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            usersettings = user.usersettings
            # Set subscription status and Stripe IDs
            usersettings.subscription_status = 'active'
            usersettings.payment_customer_id = customer_id
            usersettings.payment_subscription_id = subscription_id
            # Set the premium tier
            premium_tier = Tier.objects.get(name__iexact='Premium')
            usersettings.account_tier = premium_tier
            usersettings.save()
        except (User.DoesNotExist, Tier.DoesNotExist):
            pass  # Optionally log this

    return HttpResponse(status=200)