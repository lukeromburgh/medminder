# your_app/cron.py
# (e.g., reminders/cron.py)

import logging
from datetime import timedelta, datetime, date # Import datetime for comparisons

from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string

# Adjust these import paths based on your project structure
# It's often better to use absolute paths from the project root if cron.py is in an app.
# Assuming cron.py is within the 'reminders' app:
from .models import DailyReminderLog, Reminder # If models.py is in the same app
# Or if your models are structured differently, e.g.:
# from apps.reminders.models import DailyReminderLog, Reminder

# Assuming UserSettings is in an 'accounts' app
# from apps.accounts.models import UserSettings
# For the provided snippet, UserSettings was in '....accounts.models' relative to the command.
# Let's assume a more direct import path if 'accounts' is a top-level app.
# You'll need to verify this path based on your actual project structure.
try:
    from apps.accounts.models import UserSettings # Replace your_project_name
except ImportError:
    # Fallback if the above structure isn't quite right, adjust as needed
    # This is a common pattern if 'accounts' is an app at the same level as 'reminders'
    from apps.accounts.models import UserSettings


# --- Configure Logging (Recommended) ---
logger = logging.getLogger(__name__)
# Example basic configuration (place in your Django settings or app ready method for project-wide setup)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# If you don't set up logging, print statements will be used.

# -----------------------------------------------------------------------------
# Function 1: Send Reminders (from send_reminders.py)
# -----------------------------------------------------------------------------
def send_reminders():
    """
    Sends email reminders for upcoming medication doses, respecting timezones.
    """
    print("Cron job: Starting send_due_reminders...")
    logger.info("Cron job: Starting send_due_reminders...")

    now = timezone.localtime(timezone.now())
    time_window_minutes = 30
    time_window_end = now + timedelta(minutes=time_window_minutes)

    print(f"Checking for reminders due between {now.strftime('%Y-%m-%d %H:%M:%S %Z')} and {time_window_end.strftime('%Y-%m-%d %H:%M:%S %Z')}...")
    logger.info(f"Checking for reminders due between {now.strftime('%Y-%m-%d %H:%M:%S %Z')} and {time_window_end.strftime('%Y-%m-%d %H:%M:%S %Z')}...")

    base_filters = Q(status=DailyReminderLog.STATUS_PENDING) & \
                   Q(is_notified=False) & \
                   Q(user__usersettings__receive_email_reminders=True)

    date_filters = Q(due_date=now.date())
    if time_window_end.date() > now.date():
        date_filters |= Q(due_date=time_window_end.date())
        print(f"  Checking logs due today ({now.date()}) and tomorrow ({time_window_end.date()}).")
        logger.info(f"  Checking logs due today ({now.date()}) and tomorrow ({time_window_end.date()}).")

    else:
        print(f"  Checking logs due today ({now.date()}).")
        logger.info(f"  Checking logs due today ({now.date()}).")


    potential_reminders = DailyReminderLog.objects.filter(
        date_filters & base_filters
    ).select_related('user', 'reminder__medication', 'reminder__dosage', 'reminder__schedule')

    due_reminders = []
    for log_entry in potential_reminders:
        due_datetime_aware = log_entry.due_datetime
        if now <= due_datetime_aware < time_window_end:
            due_reminders.append(log_entry)

    if not due_reminders:
        print("No reminders found in the current window.")
        logger.info("No reminders found in the current window.")
        return

    print(f"Found {len(due_reminders)} reminders to notify.")
    logger.info(f"Found {len(due_reminders)} reminders to notify.")

    sent_count = 0
    for log_entry in due_reminders:
        user = log_entry.user
        reminder_obj = log_entry.reminder # Renamed to avoid conflict with 'Reminder' model

        if log_entry.status != DailyReminderLog.STATUS_PENDING or log_entry.is_notified:
            print(f"Skipping log entry {log_entry.id} - status not pending or already notified during final check.")
            logger.warning(f"Skipping log entry {log_entry.id} - status not pending or already notified during final check.")
            continue

        try:
            dashboard_url_path = reverse('medminder:dashboard') # Ensure 'medminder' is the correct app_name
            dashboard_url = f"{settings.SITE_URL}{dashboard_url_path}"

            context = {
                'user': user,
                'log_entry': log_entry,
                'reminder': reminder_obj,
                'dashboard_url': dashboard_url,
                'due_time_display': timezone.localtime(log_entry.due_datetime).strftime('%H:%M %Z'),
            }

            text_body = render_to_string('reminders/email/reminder_email_plain.txt', context)
            html_body = render_to_string('reminders/email/template_reminder.html', context)

            subject = f"MedMinder Reminder: Time for {reminder_obj.medication.medication_name}"
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            msg = EmailMultiAlternatives(subject, text_body, email_from, recipient_list)
            msg.attach_alternative(html_body, "text/html")
            msg.send()

            log_entry.is_notified = True
            # log_entry.notification_sent_at = timezone.now() # Already handled by model's auto_now_add or default
            log_entry.save(update_fields=['is_notified'])
            sent_count += 1
            print(f"Successfully sent email for log entry {log_entry.id} to {user.email}")
            logger.info(f"Successfully sent email for log entry {log_entry.id} to {user.email}")

        except Exception as e:
            print(f"ERROR: Failed to send email for log entry {log_entry.id} to {user.email}: {e}")
            logger.error(f"Failed to send email for log entry {log_entry.id} to {user.email}: {e}")

    print(f"Finished sending {sent_count} reminders.")
    logger.info(f"Finished sending {sent_count} reminders.")


# -----------------------------------------------------------------------------
# Function 2: Generate Upcoming Reminder Logs (from generate_upcoming_reminder_logs.py)
# -----------------------------------------------------------------------------

def _generate_expected_occurrences_for_schedule(schedule, start_date, end_date):
    """
    Helper function to calculate expected occurrence dates based on schedule rules.
    Yields date objects.
    (Moved from Command class to be a helper for the function below)
    """
    current_date = start_date
    while current_date <= end_date:
        is_an_occurrence = False
        if schedule.repeat_type == 'daily':
            is_an_occurrence = True
        elif schedule.repeat_type == 'weekly':
            selected_weekdays = [int(day) for day in schedule.weekly_days.split(',') if day]
            if current_date.weekday() in selected_weekdays: # Monday is 0 and Sunday is 6
                is_an_occurrence = True
        elif schedule.repeat_type == 'monthly':
            # Assuming monthly_dates stores day numbers (1-31) or full dates 'YYYY-MM-DD'
            # If 'YYYY-MM-DD', extract day:
            try:
                selected_days_of_month = [datetime.strptime(d, '%Y-%m-%d').day for d in schedule.monthly_dates.split(',') if d]
            except ValueError: # Handle case where it might just be day numbers
                selected_days_of_month = [int(d) for d in schedule.monthly_dates.split(',') if d]

            if current_date.day in selected_days_of_month:
                is_an_occurrence = True
        # TODO: Add logic for yearly if needed

        if schedule.end_date and current_date > schedule.end_date:
            is_an_occurrence = False # Should be caught by loop end_date but good failsafe

        if is_an_occurrence:
            yield current_date
        current_date += timedelta(days=1)


def generate_upcoming_reminder_logs():
    """
    Generates DailyReminderLog entries for upcoming reminders.
    """
    print("Cron job: Starting generate_upcoming_reminder_logs...")
    logger.info("Cron job: Starting generate_upcoming_reminder_logs...")

    today = timezone.localdate() # Use timezone aware localdate
    future_window_end = today + timedelta(days=30)

    active_reminders = Reminder.objects.filter(is_active=True).select_related('schedule', 'user')

    print(f'Starting log generation for {active_reminders.count()} active reminders up to {future_window_end}...')
    logger.info(f'Starting log generation for {active_reminders.count()} active reminders up to {future_window_end}...')


    for reminder_obj in active_reminders: # Renamed to avoid conflict
        schedule = reminder_obj.schedule
        user = reminder_obj.user # Get user from reminder

        if not schedule:
            print(f"Skipping reminder {reminder_obj.id} as it has no associated schedule.")
            logger.warning(f"Skipping reminder {reminder_obj.id} as it has no associated schedule.")
            continue

        if schedule.end_date and schedule.end_date < today:
            print(f'Skipping reminder {reminder_obj.id} as its end date ({schedule.end_date}) is in the past.')
            logger.info(f'Skipping reminder {reminder_obj.id} as its end date ({schedule.end_date}) is in the past.')
            # Optionally:
            # reminder_obj.is_active = False
            # reminder_obj.save(update_fields=['is_active'])
            continue

        generation_start_date = max(today, schedule.start_date)
        generation_end_date = future_window_end
        if schedule.end_date and schedule.end_date < generation_end_date:
            generation_end_date = schedule.end_date

        if generation_start_date > generation_end_date:
            print(f'Skipping reminder {reminder_obj.id} as generation window is invalid ({generation_start_date} to {generation_end_date}).')
            logger.info(f'Skipping reminder {reminder_obj.id} as generation window is invalid ({generation_start_date} to {generation_end_date}).')
            continue

        print(f'Generating logs for reminder {reminder_obj.id} ({user.username if user else "No User"}) from {generation_start_date} to {generation_end_date}')
        logger.info(f'Generating logs for reminder {reminder_obj.id} ({user.username if user else "No User"}) from {generation_start_date} to {generation_end_date}')


        expected_occurrences = _generate_expected_occurrences_for_schedule(
            schedule, generation_start_date, generation_end_date
        )

        logs_created_count = 0
        for occurrence_date in expected_occurrences:
            log_entry, created = DailyReminderLog.objects.get_or_create(
                reminder=reminder_obj,
                due_date=occurrence_date,
                defaults={
                    'user': user,
                    'due_time': schedule.time_of_day,
                    # 'status' defaults to DailyReminderLog.STATUS_PENDING in the model
                }
            )
            if created:
                logs_created_count +=1
                print(f'  Created log for reminder {reminder_obj.id} on {occurrence_date}')
                logger.debug(f'  Created log for reminder {reminder_obj.id} on {occurrence_date}')
        if logs_created_count > 0:
             print(f'  Finished creating {logs_created_count} logs for reminder {reminder_obj.id}.')
             logger.info(f'  Finished creating {logs_created_count} logs for reminder {reminder_obj.id}.')


    print('Log generation complete.')
    logger.info('Log generation complete.')


# -----------------------------------------------------------------------------
# Function 3: Update Missed Reminders (from update_missed_reminders.py)
# -----------------------------------------------------------------------------
def update_missed_reminders():
    """
    Finds pending reminders that are past their grace period and marks them as missed.
    """
    print("Cron job: Starting update_missed_reminders...")
    logger.info("Cron job: Starting update_missed_reminders...")

    now = timezone.now()
    logs_to_update_pks = []

    # Define a reasonable cutoff date for efficiency, e.g., logs from last 30 days.
    # Adjust as needed. If grace periods are short, a shorter cutoff might be fine.
    cutoff_date_start = now.date() - timedelta(days=30) # Check logs due in the last 30 days
    # Only consider logs up to 'now' to avoid marking future logs as missed accidentally
    cutoff_date_end = now.date()


    # Iterate over all DailyReminderLogs that are pending and within the date window.
    # This avoids loading all reminders if many have no pending logs.
    # Filter by due_date and then by the calculated due_datetime in Python.
    # Ensure grace_period is available on the Reminder model.
    # Using select_related to fetch reminder (and its grace_period) efficiently.
    pending_logs_in_window = DailyReminderLog.objects.filter(
        status=DailyReminderLog.STATUS_PENDING,
        due_date__gte=cutoff_date_start,
        due_date__lte=cutoff_date_end # Only consider logs due up to today
    ).select_related('reminder') # To access reminder.grace_period

    print(f"Found {pending_logs_in_window.count()} pending logs within the date window to check.")
    logger.info(f"Found {pending_logs_in_window.count()} pending logs within the date window to check.")


    for log in pending_logs_in_window:
        if not log.reminder: # Should not happen with select_related and proper data
            logger.warning(f"Log entry {log.pk} has no associated reminder. Skipping.")
            continue

        # Default grace period if not set on the reminder
        # Ensure reminder.grace_period is a timedelta object
        grace_period_on_reminder = getattr(log.reminder, 'grace_period', timedelta(minutes=15))
        if not isinstance(grace_period_on_reminder, timedelta):
            # Assuming grace_period is stored in minutes as an IntegerField on Reminder model
            try:
                grace_period = timedelta(minutes=int(grace_period_on_reminder))
            except (ValueError, TypeError):
                logger.warning(f"Invalid grace_period format for reminder {log.reminder.id}. Using default 15 minutes.")
                grace_period = timedelta(minutes=15) # Default grace period
        else:
            grace_period = grace_period_on_reminder


        due_datetime_aware = log.due_datetime # This is already timezone-aware

        if now > (due_datetime_aware + grace_period):
            logs_to_update_pks.append(log.pk)
            # print(f"Log {log.pk} (Due: {due_datetime_aware}) is past grace period. Marked for update.")
            # logger.debug(f"Log {log.pk} (Due: {due_datetime_aware}) is past grace period. Marked for update.")


    if logs_to_update_pks:
        updated_count = DailyReminderLog.objects.filter(pk__in=logs_to_update_pks).update(
            status=DailyReminderLog.STATUS_MISSED,
            # Optionally set a 'missed_at' timestamp here if your model has it
            # missed_at=now
        )
        message = f"Successfully marked {updated_count} reminders as missed."
        print(message)
        logger.info(message)
    else:
        message = "No pending reminders found past their grace period to mark as missed."
        print(message)
        logger.info(message)

    print('Finished update_missed_reminders job.')
    logger.info('Finished update_missed_reminders job.')
    return message # Optional: return a status message


# --- Example of how you might call these in a Django management command for cron ---
# Or if using a library like django-cron, you'd register these functions.

# In a file like your_app/management/commands/run_cron_jobs.py:
"""
from django.core.management.base import BaseCommand
# from your_app.cron import (
#     send_due_reminders,
#     generate_upcoming_reminder_logs,
#     update_missed_reminders
# )
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs all scheduled cron jobs'

    def handle(self, *args, **options):
        self.stdout.write("Running send_due_reminders...")
        try:
            send_due_reminders()
            self.stdout.write(self.style.SUCCESS("Successfully ran send_due_reminders."))
        except Exception as e:
            logger.error(f"Error running send_due_reminders: {e}", exc_info=True)
            self.stderr.write(self.style.ERROR(f"Error in send_due_reminders: {e}"))

        self.stdout.write("Running generate_upcoming_reminder_logs...")
        try:
            generate_upcoming_reminder_logs()
            self.stdout.write(self.style.SUCCESS("Successfully ran generate_upcoming_reminder_logs."))
        except Exception as e:
            logger.error(f"Error running generate_upcoming_reminder_logs: {e}", exc_info=True)
            self.stderr.write(self.style.ERROR(f"Error in generate_upcoming_reminder_logs: {e}"))

        self.stdout.write("Running update_missed_reminders...")
        try:
            update_missed_reminders()
            self.stdout.write(self.style.SUCCESS("Successfully ran update_missed_reminders."))
        except Exception as e:
            logger.error(f"Error running update_missed_reminders: {e}", exc_info=True)
            self.stderr.write(self.style.ERROR(f"Error in update_missed_reminders: {e}"))

        self.stdout.write(self.style.SUCCESS("All cron jobs finished."))
"""