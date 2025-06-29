import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import ReceiveUpdates
from unittest.mock import patch, MagicMock
from django.http import JsonResponse

from django.utils import timezone
from datetime import time, timedelta, date

from apps.accounts.models import UserSettings, Tier

User = get_user_model()


class CoreViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )

    def test_landing_page_redirects_authenticated_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("core:home"))
        # Should redirect to LOGIN_REDIRECT_URL or dashboard
        self.assertEqual(response.status_code, 200)

    def test_landing_page_get_anonymous(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing_page.html")

    def test_home_post_requires_login(self):
        response = self.client.post(reverse("core:home"), {"email": "anon@example.com"})
        self.assertContains(response, "You must be logged in to sign up for updates.")

    def test_home_post_valid_for_logged_in_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("core:home"), {"email": "test@example.com"})
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReceiveUpdates.objects.filter(user=self.user).exists())

    def test_home_post_invalid_email(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("core:home"), {"email": "not-an-email"})
        self.assertContains(response, "Please enter a valid email address.")


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.client.force_login(self.user)

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_success(self, mock_create):
        mock_create.return_value.id = "cs_test_123"
        response = self.client.get(reverse("payments:create_checkout_session"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessionId", response.json())

    def test_create_checkout_session_invalid_method(self):
        response = self.client.post(reverse("payments:create_checkout_session"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.json())

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_success_view_with_session(self, mock_retrieve):
        mock_retrieve.return_value = {"customer_details": {"email": "test@example.com"}}
        response = self.client.get(
            reverse("payments:payment_success") + "?session_id=cs_test_123"
        )
        self.assertTemplateUsed(response, "payments/success.html")
        self.assertIn("customer_email", response.context)

    def test_payment_success_view_without_session(self):
        response = self.client.get(reverse("payments:payment_success"))
        self.assertTemplateUsed(response, "payments/success.html")
        self.assertIsNone(response.context["customer_email"])

    def test_payment_cancel_view(self):
        response = self.client.get(reverse("payments:payment_cancel"))
        self.assertTemplateUsed(response, "payments/cancel.html")

    def test_product_landing_page_view(self):
        response = self.client.get("/payments/")
        self.assertTemplateUsed(response, "payments/product_page.html")
        self.assertIn("stripe_publishable_key", response.context)
        self.assertIn("health_hero_price_id", response.context)

    def test_stripe_config_get(self):
        response = self.client.get(reverse("payments:stripe_config"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("publicKey", response.json())


class StripeWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.usersettings, _ = UserSettings.objects.get_or_create(user=self.user)
        self.secret = "whsec_test"

    @patch("stripe.Webhook.construct_event")
    def test_webhook_checkout_session_completed_updates_user(self, mock_construct):
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_details": {"email": self.user.email},
                    "customer": "cus_123",
                    "subscription": "sub_456",
                }
            },
        }
        mock_construct.return_value = mock_event

        response = self.client.post(
            reverse("payments:stripe-webhook"),
            data=json.dumps(mock_event),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy_signature",
        )

        self.assertEqual(response.status_code, 200)
        self.usersettings.refresh_from_db()
        self.assertEqual(self.usersettings.subscription_status, "premium")
        self.assertEqual(self.usersettings.payment_customer_id, "cus_123")
        self.assertEqual(self.usersettings.payment_subscription_id, "sub_456")
        self.assertEqual(self.usersettings.account_tier.name, "Premium")

    def test_webhook_without_signature(self):
        response = self.client.post(
            reverse("payments:stripe-webhook"),
            data=json.dumps({"dummy": "data"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_invalid_event_type(self, mock_construct):
        mock_construct.return_value = {"type": "other.event"}
        response = self.client.post(
            reverse("payments:stripe-webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy_signature",
        )
        self.assertEqual(response.status_code, 200)

    @patch("stripe.Webhook.construct_event", side_effect=ValueError("Invalid payload"))
    def test_webhook_invalid_payload(self, mock_construct):
        response = self.client.post(
            reverse("payments:stripe-webhook"),
            data="invalid json",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy_signature",
        )
        self.assertEqual(response.status_code, 400)


class AccountViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("accounts:signup_user")
        self.login_url = reverse("accounts:login_user")
        self.logout_url = reverse("accounts:logout")
        self.signup_page_url = reverse("accounts:signup")
        self.login_page_url = reverse("accounts:login")
        self.manage_plan_url = reverse("accounts:manage_plan")

        self.valid_user_data = {
            "username": "test@example.com",
            "email": "test@example.com",
            "password": "StrongPass123!",  # Single password field
        }

        self.valid_login_data = {
            "username": self.valid_user_data["email"],
            "password": self.valid_user_data["password"],
        }

    def test_signup_page_renders(self):
        response = self.client.get(self.signup_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup_page.html")

    def test_login_page_renders(self):
        response = self.client.get(self.login_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login_page.html")

    def test_manage_plan_redirects(self):
        User.objects.create_user(
            username="testuser",
            email=self.valid_user_data["email"],
            password=self.valid_user_data["password"],
        )
        self.client.login(
            username=self.valid_user_data["email"],
            password=self.valid_user_data["password"],
        )
        response = self.client.get(self.manage_plan_url)
        self.assertEqual(response.status_code, 302)  # Redirect is expected
        # Optional: assert destination URL if you know it
        # self.assertRedirects(response, expected_url)

    def test_signup_user_valid_post(self):
        response = self.client.post(self.signup_url, data=self.valid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "redirect": reverse("medminder:dashboard")},
        )
        self.assertTrue(
            User.objects.filter(email=self.valid_user_data["email"]).exists()
        )

    def test_login_user_valid(self):
        User.objects.create_user(
            username=self.valid_user_data["username"],
            email=self.valid_user_data["email"],
            password=self.valid_user_data["password"],
        )
        response = self.client.post(self.login_url, data=self.valid_login_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "redirect": reverse("medminder:dashboard")},
        )

    def test_login_user_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            data={"username": "wrong@example.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertFalse(json["success"])
        self.assertIn("errors", json)

    def test_login_user_invalid_form(self):
        response = self.client.post(
            self.login_url, data={"username": "only@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertFalse(json["success"])
        self.assertIn("errors", json)


#  ---------------------------------------------------------------------------------------- #
# ----------------- Reminder Views Tests -----------------#

from apps.reminders.models import (
    Medication,
    Dosage,
    Schedule,
    Reminder,
    DailyReminderLog,
    UserStats,
)
from apps.reminders.views import dashboard_today
from apps.reminders.views import (
    get_user_tier,
    calculate_current_adherence_streak,
)  # Assuming these exist

User = get_user_model()


class DashboardTodayViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.med = Medication.objects.create(medication_name="MedA")
        self.dosage = Dosage.objects.create(dosage="10mg")

        self.today = timezone.localdate()
        self.now = timezone.localtime(timezone.now()).time()

    def create_schedule(self, **kwargs):
        defaults = {
            "repeat_type": "daily",
            "time_of_day": time(9, 0),
            "start_date": self.today - timedelta(days=1),
            "end_date": None,
            "weekly_days": "",
            "monthly_dates": "",
        }
        defaults.update(kwargs)
        return Schedule.objects.create(**defaults)

    def create_reminder(self, schedule, is_active=True):
        return Reminder.objects.create(
            user=self.user,
            medication=self.med,
            dosage=self.dosage,
            schedule=schedule,
            is_active=is_active,
        )

    def make_request(self):
        request = self.factory.get("/dashboard/today/")
        request.user = self.user
        return request

    @patch("django.urls.reverse", return_value="/fake-url/")
    def test_daily_reminder_creates_log(self, mock_reverse):
        schedule = self.create_schedule(repeat_type="daily")
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        response = dashboard_today(request)

        self.assertEqual(response.status_code, 200)

        logs = DailyReminderLog.objects.filter(user=self.user, due_date=self.today)
        self.assertTrue(logs.exists())
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().reminder, reminder)
        self.assertEqual(logs.first().status, "pending")


    @patch("django.urls.reverse", return_value="/fake-url/")
    def test_weekly_reminder_due_today_creates_log(self, mock_reverse):
        # Set weekly_days to include today's weekday
        weekday_str = str(self.today.weekday())
        schedule = self.create_schedule(repeat_type="weekly", weekly_days=weekday_str)
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertTrue(logs.exists())

    @patch("django.urls.reverse", return_value="/fake-url/")
    def test_weekly_reminder_not_due_today_no_log(self, mock_reverse):
        # weekly_days does not include today's weekday
        other_day = (self.today.weekday() + 1) % 7
        schedule = self.create_schedule(
            repeat_type="weekly", weekly_days=str(other_day)
        )
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertFalse(logs.exists())

    def test_monthly_reminder_due_today_creates_log(self):
        schedule = self.create_schedule(
            repeat_type="monthly", monthly_dates=str(self.today.day)
        )
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertTrue(logs.exists())

    def test_monthly_reminder_not_due_today_no_log(self):
        # monthly_dates does not include today
        schedule = self.create_schedule(
            repeat_type="monthly", monthly_dates="1"
        )  # If today is not 1st
        if self.today.day == 1:
            schedule.monthly_dates = "2"
            schedule.save()
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertFalse(logs.exists())

    def test_reminder_past_end_date_no_log(self):
        schedule = self.create_schedule(end_date=self.today - timedelta(days=1))
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertFalse(logs.exists())

    def test_reminder_with_invalid_weekly_days_no_log(self):
        schedule = self.create_schedule(repeat_type="weekly", weekly_days="a,b,c")
        reminder = self.create_reminder(schedule)

        request = self.make_request()
        dashboard_today(request)

        logs = DailyReminderLog.objects.filter(
            user=self.user, due_date=self.today, reminder=reminder
        )
        self.assertFalse(logs.exists())

    def test_next_reminder_returns_correct_log(self):
        schedule = self.create_schedule(
            repeat_type="daily",
            time_of_day=(timezone.localtime(timezone.now()) + timedelta(hours=1)).time(),
        )
        reminder = self.create_reminder(schedule)

        log = DailyReminderLog.objects.create(
            user=self.user,
            reminder=reminder,
            due_date=self.today,
            due_time=schedule.time_of_day,
            status="pending",
        )

        self.client.force_login(self.user)  # Needed if your view uses login_required
        response = self.client.get(reverse("medminder:dashboard"))  # Uses the URL name

        self.assertEqual(response.status_code, 200)
        self.assertIn("next_reminder", response.context)
        self.assertEqual(response.context["next_reminder"], log)


    # Add more tests for adherence, achievement points, streak, etc. as needed
