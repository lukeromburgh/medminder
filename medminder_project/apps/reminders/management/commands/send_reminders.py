# apps/reminders/management/commands/send_reminders.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta, datetime  # Import datetime for comparisons
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string

from ...models import DailyReminderLog  # Import your models
from ....accounts.models import (
    UserSettings,
)  # Import UserSettings model (assuming this path)

# from django.contrib.auth import get_user_model
# User = get_user_model()


class Command(BaseCommand):
    help = "Sends email reminders for upcoming medication doses, respecting timezones."

    def handle(self, *args, **options):
        # Get the current timezone-aware time
        now = timezone.localtime(timezone.now())
        time_window_minutes = 30
        # Calculate the end of the notification window (timezone-aware)
        time_window_end = now + timedelta(minutes=time_window_minutes)

        self.stdout.write(
            f"Checking for reminders due between {now.strftime('%Y-%m-%d %H:%M:%S %Z')} and {time_window_end.strftime('%Y-%m-%d %H:%M:%S %Z')}..."
        )

        # Base filters for pending, not notified, and email enabled users
        base_filters = (
            Q(status=DailyReminderLog.STATUS_PENDING)
            & Q(is_notified=False)
            & Q(user__usersettings__receive_email_reminders=True)
        )

        # --- Timezone-aware filtering using due_datetime property ---
        # We need to filter logs whose combined due_date and due_time (as a timezone-aware datetime)
        # falls within the notification window [now, time_window_end].
        # This is more complex to do purely in a Django ORM filter on DateField/TimeField.
        # A more reliable approach is to filter by date first and then check the full datetime in Python.
        # Filter logs due today or tomorrow if the window crosses midnight
        date_filters = Q(due_date=now.date())
        if time_window_end.date() > now.date():
            date_filters |= Q(due_date=time_window_end.date())
            self.stdout.write(
                f"  Checking logs due today ({now.date()}) and tomorrow ({time_window_end.date()})."
            )
        else:
            self.stdout.write(f"  Checking logs due today ({now.date()}).")

        # Initial query to get potentially relevant logs based on date and base filters
        potential_reminders = DailyReminderLog.objects.filter(
            date_filters & base_filters
        ).select_related(
            "user", "reminder__medication", "reminder__dosage", "reminder__schedule"
        )  # Select related for efficiency

        due_reminders = []
        # Iterate and filter based on the full timezone-aware due_datetime
        for log_entry in potential_reminders:
            due_datetime_aware = (
                log_entry.due_datetime
            )  # Use the timezone-aware property

            # Check if the timezone-aware due_datetime falls within the timezone-aware window
            if now <= due_datetime_aware < time_window_end:
                # Add a small buffer to the upper bound to include the exact end time if needed,
                # depending on how precise you need the window to be.
                # For < time_window_end, it excludes the exact end time.
                # If you want to include the exact end time, use <= time_window_end.
                # Let's stick to < for a 30-minute window *starting* now.
                due_reminders.append(log_entry)

        if not due_reminders:
            self.stdout.write("No reminders found in the current window.")
            return

        self.stdout.write(f"Found {len(due_reminders)} reminders to notify.")

        sent_count = 0
        for log_entry in due_reminders:
            user = log_entry.user
            reminder = log_entry.reminder

            # Double-check status and notification flag before sending
            if (
                log_entry.status != DailyReminderLog.STATUS_PENDING
                or log_entry.is_notified
            ):
                self.stdout.write(
                    f"Skipping log entry {log_entry.id} - status not pending or already notified during final check."
                )
                continue  # Skip if status changed or already notified since initial query

            # --- Generate the Dashboard URL ---
            # Use the 'dashboard' URL name
            dashboard_url_path = reverse("medminder:dashboard")
            # Build the absolute URL using the SITE_URL setting
            # Ensure settings.SITE_URL is configured in your settings.py
            dashboard_url = f"{settings.SITE_URL}{dashboard_url_path}"
            # -----------------------------------

            # --- Render the email templates ---
            context = {
                "user": user,
                "log_entry": log_entry,
                "reminder": reminder,  # Passing the reminder object directly
                "dashboard_url": dashboard_url,  # Pass the generated dashboard URL to the template
                # Pass the timezone-aware due time for display in the email
                "due_time_display": timezone.localtime(log_entry.due_datetime).strftime(
                    "%H:%M %Z"
                ),
            }

            # Render plain text and HTML versions
            text_body = render_to_string(
                "reminders/email/reminder_email_plain.txt", context
            )
            html_body = render_to_string(
                "reminders/email/template_reminder.html", context
            )
            # ------------------------------------

            subject = (
                f"MedMinder Reminder: Time for {reminder.medication.medication_name}"
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            try:
                msg = EmailMultiAlternatives(
                    subject, text_body, email_from, recipient_list
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()

                log_entry.is_notified = True  # Mark as notified
                # Use timezone.now() for the timestamp, it will be stored as UTC by Django
                # log_entry.notification_sent_at = timezone.now()
                # Don't mark as completed here, as completion happens via the dashboard manually
                log_entry.save(
                    update_fields=["is_notified"]
                )  # Use update_fields for efficiency
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully sent email for log entry {log_entry.id} to {user.email}"
                    )
                )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send email for log entry {log_entry.id} to {user.email}: {e}"
                    )
                )
                # You might want to add logging or retry logic here

        self.stdout.write(
            self.style.SUCCESS(f"Finished sending {sent_count} reminders.")
        )
