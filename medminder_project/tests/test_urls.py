from django.test import TestCase, Client
from django.urls import NoReverseMatch, reverse, resolve
from django.contrib.admin.sites import site as admin_site
from apps.reminders import views as reminders_views
from apps.payments import views as payments_views
from apps.accounts import views as accounts_views


class MainURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_admin_url_resolves(self):
        resolver = resolve('/admin/')
        self.assertEqual(resolver.func.__module__, admin_site.__class__.__module__)

    def test_core_urls(self):
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])

    def test_accounts_urls(self):
        response = self.client.get('/accounts/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_reminders_urls(self):
        response = self.client.get('/medminder/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_browser_reload(self):
        response = self.client.get('/__reload__/')
        self.assertIn(response.status_code, [200, 404])

    def test_payments_urls(self):
        response = self.client.get('/payments/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_documentation_urls(self):
        response = self.client.get('/documentation/')
        self.assertIn(response.status_code, [200, 302, 404])

    def test_all_documentation_urls(self):
        urls = [
            'home',
            'overview',
            'the-why',
            'design-deep-dive',
            'under-the-hood',
            'strategy-plane',
            'scope-plane',
            'structure-plane',
            'skeleton-plane',
            'surface-plane',
            'user-stories'
        ]
        for url_name in urls:
            with self.subTest(url=url_name):
                try:
                    url = reverse(f'documentation:{url_name}')
                    response = self.client.get(url)
                    self.assertIn(
                        response.status_code,
                        [200, 302, 404],
                        msg=f"URL documentation:{url_name} returned {response.status_code}"
                    )
                except NoReverseMatch:
                    self.fail(f"Reverse match failed for documentation:{url_name}")


class MedminderURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dummy_reminder_id = 1  # You may need to create a real object depending on your view logic

        self.urls = [
            ('medminder:dashboard', None),
            ('medminder:new_plan', None),
            ('medminder:add_reminder', None),
            ('medminder:reminder_success', None),
            ('medminder:complete_reminder', [self.dummy_reminder_id]),
            ('medminder:medications', None),
            ('medminder:dashboard_calendar', None),
            ('medminder:account_page', None),
            ('medminder:update_user_settings', None),
            ('medminder:manage_plan', None),
            ('medminder:delete_reminder', [self.dummy_reminder_id]),
            ('medminder:viewers', None),
        ]

    def test_all_urls(self):
        for name, args in self.urls:
            with self.subTest(url=name):
                try:
                    url = reverse(name, args=args) if args else reverse(name)
                    response = self.client.get(url)
                    self.assertIn(
                        response.status_code,
                        [200, 302, 403, 404],
                        msg=f"{name} returned {response.status_code}"
                    )
                except NoReverseMatch:
                    self.fail(f"Reverse match failed for {name}")


class PaymentsURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = [
            ('payments:create_checkout_session', None),
            ('payments:product_landing_page', None),
            ('payments:payment_success', None),
            ('payments:payment_cancel', None),
            ('payments:stripe_config', None),
            ('payments:stripe-webhook', None),
        ]

    def test_all_payments_urls(self):
        for name, args in self.urls:
            with self.subTest(url=name):
                try:
                    url = reverse(name, args=args) if args else reverse(name)
                    response = self.client.get(url)
                    self.assertIn(
                        response.status_code,
                        [200, 302, 403, 400, 404],
                        msg=f"{name} returned unexpected status code {response.status_code}."
                    )
                except NoReverseMatch:
                    self.fail(f"Reverse match failed for {name}")


class AccountsURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = [
            ('accounts:login', None),
            ('accounts:login_user', None),
            ('accounts:manage_plan', None),
        ]

    def test_accounts_urls(self):
        for name, args in self.urls:
            with self.subTest(url=name):
                try:
                    url = reverse(name, args=args) if args else reverse(name)
                    response = self.client.get(url)
                    self.assertIn(
                        response.status_code,
                        [200, 302, 403, 400, 404],
                        msg=f"{name} returned unexpected status code {response.status_code}."
                    )
                except NoReverseMatch:
                    self.fail(f"Reverse match failed for {name}")
