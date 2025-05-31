import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt # Only for simplicity in this example

# Initialize Stripe with your secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Replace this with your actual Price ID from the Stripe Dashboard
HEALTH_HERO_PRICE_ID = 'price_YOUR_HEALTH_HERO_PRICE_ID' # <<< IMPORTANT: Update this!

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "[http://127.0.0.1:8000](http://127.0.0.1:8000)" # Change to your domain in production
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': HEALTH_HERO_PRICE_ID,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/payments/success/',
                cancel_url=YOUR_DOMAIN + '/payments/cancel/',
            )
            # In a real application, you might want to save checkout_session.id
            # to your database associated with the user or order.
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            print(f"Error creating Stripe session: {e}")
            return HttpResponse(f"Error: {e}", status=500)

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
