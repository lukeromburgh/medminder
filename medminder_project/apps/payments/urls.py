from django.urls import path
from .views import (
    create_checkout_session,
    payment_success_view,
    payment_cancel_view,
    product_landing_page_view,
    stripe_config,
    stripe_webhook,
)

app_name = "payments"


urlpatterns = [
    # path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path(
        "create-checkout-session/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path("", product_landing_page_view, name="product_landing_page"),
    path("success/", payment_success_view, name="payment_success"),
    path("cancelled/", payment_cancel_view, name="payment_cancel"),
    path("config/", stripe_config, name="stripe_config"),
    path("stripe-webhook/", stripe_webhook, name="stripe-webhook"),
]
