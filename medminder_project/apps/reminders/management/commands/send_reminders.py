# reminders/management/commands/send_reminders.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.urls import reverse # Import reverse
from django.conf import settings # Import settings
from django.template.loader import render_to_string

from ...models import DailyReminderLog # Import your models
from ....accounts.models import UserSettings # Import User model (assuming this path)
# from django.contrib.auth import get_user_model
# User = get_user_model()


class Command(BaseCommand):
    help = 'Sends email reminders for upcoming medication doses.'

    def handle(self, *args, **options):
        now = timezone.localtime(timezone.now())
        time_window_minutes = 30
        time_window_end = now + timedelta(minutes=time_window_minutes)

        self.stdout.write(f"Checking for reminders due today ({now.date().strftime('%Y-%m-%d')}) within the window starting from {now.time().strftime('%H:%M')} for the next {time_window_minutes} minutes...")

        base_filters = Q(status='pending') & Q(is_notified=False) & Q(user__usersettings__receive_email_reminders=True)

        time_range_q = Q()
        if time_window_end.date() == now.date():
            time_range_q = Q(due_time__gte=now.time(), due_time__lte=time_window_end.time())
            self.stdout.write(f"  Filtering today between {now.time().strftime('%H:%M')} and {time_window_end.time().strftime('%H:%M')}.")
        elif time_window_end.date() > now.date():
             time_range_q = Q(Q(due_time__gte=now.time()) | Q(due_time__lte=time_window_end.time()))
             self.stdout.write(f"  Filtering today (across midnight) >= {now.time().strftime('%H:%M')} OR <= {time_window_end.time().strftime('%H:%M')}.")


        due_reminders = DailyReminderLog.objects.filter(
            Q(due_date=now.date()) & base_filters & time_range_q
        ).select_related('user', 'reminder__medication', 'reminder__dosage', 'reminder__schedule')


        if not due_reminders:
            self.stdout.write("No reminders found in the current window.")
            return

        self.stdout.write(f"Found {due_reminders.count()} reminders to notify.")

        sent_count = 0
        for log_entry in due_reminders:
            user = log_entry.user
            reminder = log_entry.reminder

            if log_entry.status != 'pending' or log_entry.is_notified:
                self.stdout.write(f"Skipping log entry {log_entry.id} - status not pending or already notified.")
                continue

            # --- Generate the Dashboard URL ---
            # Use the 'dashboard' URL name
            dashboard_url_path = reverse('medminder:dashboard')
            # Build the absolute URL using the SITE_URL setting
            dashboard_url = f"{settings.SITE_URL}{dashboard_url_path}"
            # -----------------------------------


            # --- Render the email templates ---
            context = {
                'user': user,
                'log_entry': log_entry,
                'reminder': reminder, # Passing the reminder object directly
                'dashboard_url': dashboard_url, # Pass the generated dashboard URL to the template
            }

            # Render plain text and HTML versions
            text_body = render_to_string('reminders/email/reminder_email_plain.txt', context)
            html_body = render_to_string('reminders/email/reminder_email.html', context)
            # ------------------------------------


            subject = f"MedMinder Reminder: Time for {reminder.medication.medication_name}"
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            try:
                msg = EmailMultiAlternatives(subject, text_body, email_from, recipient_list)
                msg.attach_alternative(html_body, "text/html")
                msg.send()

                log_entry.is_notified = True # Mark as notified
                log_entry.notification_sent_at = timezone.localtime(timezone.now()) # Record notification time
                # Don't mark as completed here, as completion happens via the dashboard manually
                log_entry.save()
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f"Successfully sent email for log entry {log_entry.id} to {user.email}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to send email for log entry {log_entry.id} to {user.email}: {e}"))
                # You might want to add logging or retry logic here

        self.stdout.write(self.style.SUCCESS(f"Finished sending {sent_count} reminders."))