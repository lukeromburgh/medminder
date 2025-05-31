from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    payment_success_view,
    payment_cancel_view,
    product_landing_page_view
)

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('', product_landing_page_view, name='product_landing_page'),
    path('success/', payment_success_view, name='payment_success'),
    path('cancel/', payment_cancel_view, name='payment_cancel'),
]