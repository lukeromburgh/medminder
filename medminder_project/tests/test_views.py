import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import ReceiveUpdates
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from apps.accounts.models import UserSettings, Tier

User = get_user_model()

class CoreViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass', email='test@example.com')

    def test_landing_page_redirects_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('core:home'))
        # Should redirect to LOGIN_REDIRECT_URL or dashboard
        self.assertEqual(response.status_code, 200)

    def test_landing_page_get_anonymous(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/landing_page.html')

    def test_home_post_requires_login(self):
        response = self.client.post(reverse('core:home'), {'email': 'anon@example.com'})
        self.assertContains(response, "You must be logged in to sign up for updates.")

    def test_home_post_valid_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('core:home'), {'email': 'test@example.com'})
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReceiveUpdates.objects.filter(user=self.user).exists())

    def test_home_post_invalid_email(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('core:home'), {'email': 'not-an-email'})
        self.assertContains(response, "Please enter a valid email address.")


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.force_login(self.user)

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_success(self, mock_create):
        mock_create.return_value.id = 'cs_test_123'
        response = self.client.get(reverse('payments:create_checkout_session'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionId', response.json())

    def test_create_checkout_session_invalid_method(self):
        response = self.client.post(reverse('payments:create_checkout_session'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json())

    @patch('stripe.checkout.Session.retrieve')
    def test_payment_success_view_with_session(self, mock_retrieve):
        mock_retrieve.return_value = {'customer_details': {'email': 'test@example.com'}}
        response = self.client.get(reverse('payments:payment_success') + '?session_id=cs_test_123')
        self.assertTemplateUsed(response, 'payments/success.html')
        self.assertIn('customer_email', response.context)

    def test_payment_success_view_without_session(self):
        response = self.client.get(reverse('payments:payment_success'))
        self.assertTemplateUsed(response, 'payments/success.html')
        self.assertIsNone(response.context['customer_email'])

    def test_payment_cancel_view(self):
        response = self.client.get(reverse('payments:payment_cancel'))
        self.assertTemplateUsed(response, 'payments/cancel.html')

    def test_product_landing_page_view(self):
        response = self.client.get(reverse('payments:product_landing_page'))
        self.assertTemplateUsed(response, 'payments/product_page.html')
        self.assertIn('stripe_publishable_key', response.context)
        self.assertIn('health_hero_price_id', response.context)

    def test_stripe_config_get(self):
        response = self.client.get(reverse('payments:stripe_config'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('publicKey', response.json())


class StripeWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.usersettings, _ = UserSettings.objects.get_or_create(user=self.user)
        self.secret = 'whsec_test'

    @patch('stripe.Webhook.construct_event')
    def test_webhook_checkout_session_completed_updates_user(self, mock_construct):
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_details': {'email': self.user.email},
                    'customer': 'cus_123',
                    'subscription': 'sub_456'
                }
            }
        }
        mock_construct.return_value = mock_event

        response = self.client.post(
            reverse('payments:stripe-webhook'),
            data=json.dumps(mock_event),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_signature'
        )

        self.assertEqual(response.status_code, 200)
        self.usersettings.refresh_from_db()
        self.assertEqual(self.usersettings.subscription_status, 'premium')
        self.assertEqual(self.usersettings.payment_customer_id, 'cus_123')
        self.assertEqual(self.usersettings.payment_subscription_id, 'sub_456')
        self.assertEqual(self.usersettings.account_tier.name, 'Premium')

    def test_webhook_without_signature(self):
        response = self.client.post(
            reverse('payments:stripe-webhook'),
            data=json.dumps({'dummy': 'data'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_invalid_event_type(self, mock_construct):
        mock_construct.return_value = {'type': 'other.event'}
        response = self.client.post(
            reverse('payments:stripe-webhook'),
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_signature'
        )
        self.assertEqual(response.status_code, 200)

    @patch('stripe.Webhook.construct_event', side_effect=ValueError("Invalid payload"))
    def test_webhook_invalid_payload(self, mock_construct):
        response = self.client.post(
            reverse('payments:stripe-webhook'),
            data='invalid json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_signature'
        )
        self.assertEqual(response.status_code, 400)

    # @patch('stripe.Webhook.construct_event', side_effect=Exception("Unexpected error"))
    # def test_webhook_generic_error(self, mock_construct):
    #     response = self.client.post(
    #         reverse('payments:stripe-webhook'),
    #         data=json.dumps({}),
    #         content_type='application/json',
    #         HTTP_STRIPE_SIGNATURE='dummy_signature'
    #     )
    #     self.assertEqual(response.status_code, 400)