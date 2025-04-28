from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta, time # Import time
from django.db.models import Q # Import Q object
from ...models import DailyReminderLog # Import your models
from ....accounts.models import UserSettings # Import User model
from django.template.loader import render_to_string
from django.conf import settings # Import settings


class Command(BaseCommand):
    help = 'Sends email reminders for upcoming medication doses.'

    def handle(self, *args, **options):
        now = timezone.localtime(timezone.now()) # Get current datetime in local timezone
        # Define a time window for reminders, e.g., due within the next 30 minutes
        time_window_minutes = 30
        time_window_end = now + timedelta(minutes=time_window_minutes)

        # Determine the start and end times for the filter based on the current time
        start_time = now.time()
        end_time = time_window_end.time() # This will be tomorrow's time if window crosses midnight

        self.stdout.write(f"Checking for reminders due today ({now.date().strftime('%Y-%m-%d')}) within the window starting from {start_time.strftime('%H:%M')} for the next {time_window_minutes} minutes...")
        # Note: The time range displayed here might be confusing if it crosses midnight,
        # but the query logic below handles it correctly for today's date.

        # Base filters that apply
        base_filters = Q(status='pending') & Q(is_notified=False) & Q(user__usersettings__receive_email_reminders=True)

        # Time range filters for today's date, handling wrap-around
        time_range_q = Q()

        # If the window does *not* cross midnight (e.g., 10:00 to 10:30)
        if time_window_end.date() == now.date():
            time_range_q = Q(
                due_time__gte=start_time,
                due_time__lte=end_time
            )
            self.stdout.write(f"  Filtering today between {start_time.strftime('%H:%M')} and {end_time.strftime('%H:%M')}.")


        # If the window *does* cross midnight (e.g., 23:45 to 00:15)
        # We still only want reminders for TODAY's date.
        # The time filter needs to find times >= start_time OR <= end_time *on today's date*.
        elif time_window_end.date() > now.date():
             # The reminders must be on the current date
             # And their time must be >= the start time OR <= the end time (wrapping around midnight)
             time_range_q = Q(
                Q(due_time__gte=start_time) | Q(due_time__lte=end_time)
             )
             self.stdout.write(f"  Filtering today (across midnight) >= {start_time.strftime('%H:%M')} OR <= {end_time.strftime('%H:%M')}.")


        # Combine the date filter, base filters, and the time range filters
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

            # Check one last time just in case the status changed concurrently
            if log_entry.status != 'pending' or log_entry.is_notified:
                self.stdout.write(f"Skipping log entry {log_entry.id} - status not pending or already notified.")
                continue

            # ... (rest of your email sending logic remains the same) ...
            subject = f"MedMinder Reminder: Time for {reminder.medication.medication_name}"
            message = (
                f"Hi {user.username},\n\n"
                f"This is a reminder to take your medication:\n\n"
                f"Medication: {reminder.medication.medication_name}\n"
                f"Dosage: {reminder.dosage.dosage}\n"
                f"Time: {log_entry.due_time.strftime('%H:%M')}\n\n"
                f"Remember to log completion on your dashboard.\n\n"
                f"Best regards,\nMedMinder Team"
            )

            email_from = settings.DEFAULT_FROM_EMAIL # Make sure DEFAULT_FROM_EMAIL is set in settings.py
            recipient_list = [user.email]

            try:
                send_mail(subject, message, email_from, recipient_list)
                log_entry.is_notified = True # Mark as notified
                log_entry.save()
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(f"Successfully sent email for log entry {log_entry.id} to {user.email}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to send email for log entry {log_entry.id} to {user.email}: {e}"))
                # You might want to add logging or retry logic here

        self.stdout.write(self.style.SUCCESS(f"Finished sending {sent_count} reminders."))