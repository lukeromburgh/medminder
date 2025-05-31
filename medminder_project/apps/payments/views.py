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
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
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
    # Here you would typically:
    # 1. Verify the session if using webhooks (recommended for production).
    # 2. Fulfill the order (e.g., grant access to "Health Hero").
    # 3. Display a success message to the user.
    return render(request, 'payments/success.html')

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