from django.shortcuts import render, redirect
from django.conf import settings
import stripe

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

def CreateCheckoutSessionView(request):
    if request.method == 'POST':
        YOUR_DOMAIN = "http://localhost:8000"  # Adjust this to your domain
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': 'price_1N4k2eLz5Z3y7e8X9Y5Z5Z5Z',  # Replace with your actual price ID
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url, code=303)
    return render(request, 'payments/create_checkout_session.html')