import logging
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib.auth.models import User
import pytz
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.db import DatabaseError
import smtplib
import os

from .models import DailyReminderLog, Reminder, UserStats
from .views import calculate_current_adherence_streak
from apps.accounts.models import UserSettings

# Configure logger to write to the project root (one level above BASE_DIR) and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplication
logger.handlers = []

# Define formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

# FileHandler to write to project_root/cron.log (one level above BASE_DIR)
project_root = os.path.dirname(settings.BASE_DIR)  # Parent of BASE_DIR
log_file = os.path.join(project_root, 'cron.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info(f"Logging configured to write to {log_file} and console")

# --- Reusable Email Sending Function ---
def send_email_template(subject, template_name, context, recipient, from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Sends an email using the specified template and context.

    :param subject: Email subject
    :param template_name: Base name of the template (without .txt/.html extension)
    :param context: Context dictionary for template rendering
    :param recipient: Recipient's email address
    :param from_email: Sender's email address (default: settings.DEFAULT_FROM_EMAIL)
    """
    try:
        text_body = render_to_string(f"reminders/email/{template_name}.txt", context)
        html_body = render_to_string(f"reminders/email/{template_name}.html", context)
        msg = EmailMultiAlternatives(subject, text_body, from_email, [recipient])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        logger.info(f"Sent email '{subject}' to {recipient}")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email '{subject}' to {recipient}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error sending email '{subject}' to {recipient}: {e}", exc_info=True)

# --- Function 1: Send Reminders ---
def send_reminders():
    """
    Sends email reminders for medication doses due within the next 15 minutes.
    Uses user-specific time zones from UserSettings, with UTC fallback if unavailable.
    Skips users who have disabled email reminders.
    """
    now_utc = timezone.now()
    logger.info(f"[{now_utc.isoformat()}] Starting send_reminders job...")

    reminders = DailyReminderLog.objects.filter(
        status=DailyReminderLog.STATUS_PENDING,
        is_notified=False
    ).select_related(
        'user', 'user__usersettings', 'reminder', 'reminder__medication'
    )

    if not reminders.exists():
        logger.info(f"[{now_utc.isoformat()}] No pending medication reminders to process.")
        return

    sent_count = 0
    processed_count = 0

    for reminder in reminders:
        processed_count += 1
        target_user = reminder.user

        try:
            # Get user-specific time zone with fallback to UTC
            try:
                user_settings = target_user.usersettings
                user_tz = pytz.timezone(user_settings.timezone or 'UTC')
            except (User.usersettings.RelatedObjectDoesNotExist, pytz.exceptions.UnknownTimeZoneError):
                logger.warning(f"No valid timezone for user {target_user.username} (ID: {target_user.id}). Using UTC.")
                user_tz = pytz.UTC

            # Combine due_date and due_time into a naive datetime
            naive_due_datetime = datetime.combine(reminder.due_date, reminder.due_time)
            # Localize to user's time zone (override default timezone in due_datetime property)
            local_due_datetime = user_tz.localize(naive_due_datetime)
            now_in_user_tz = now_utc.astimezone(user_tz)
            time_difference = (local_due_datetime - now_in_user_tz).total_seconds()

            logger.debug(f"[{now_utc.isoformat()}] Reminder ID {reminder.id}: due {local_due_datetime.isoformat()}, now {now_in_user_tz.isoformat()}, diff {time_difference}s")

            if not user_settings.receive_email_reminders:
                logger.info(f"[{now_utc.isoformat()}] User {target_user.username} has disabled email reminders. Skipping reminder ID {reminder.id}.")
                continue

            # Check if reminder is due within the next 15 minutes (configurable window)
            REMINDER_WINDOW_SECONDS = 900  # 15 minutes
            if 0 <= time_difference <= REMINDER_WINDOW_SECONDS:
                if reminder.is_notified:
                    logger.info(f"[{now_utc.isoformat()}] Reminder ID {reminder.id} already notified for {target_user.username}. Skipping.")
                    continue

                dashboard_url = f"{settings.SITE_URL}{reverse('medminder:dashboard')}"
                context = {
                    'user': target_user,
                    'log_entry': reminder,
                    'reminder': reminder.reminder,
                    'dashboard_url': dashboard_url,
                    'due_time_display': local_due_datetime.strftime('%H:%M %Z'),
                }

                send_email_template(
                    subject=f"MedMinder Reminder: Time for {reminder.reminder.medication.medication_name}",
                    template_name="template_reminder",
                    context=context,
                    recipient=target_user.email
                )

                try:
                    reminder.is_notified = True
                    reminder.save(update_fields=['is_notified'])
                    sent_count += 1
                except DatabaseError as e:
                    logger.error(f"[{now_utc.isoformat()}] Failed to update is_notified for reminder ID {reminder.id}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"[{now_utc.isoformat()}] Error processing reminder ID {reminder.id} for {target_user.username}: {e}", exc_info=True)

    logger.info(f"[{now_utc.isoformat()}] Finished. Processed {processed_count} reminders. Sent {sent_count} new reminders.")

# --- Function 2: Generate Upcoming Reminder Logs ---
def generate_upcoming_reminder_logs():
    """
    Generates DailyReminderLog entries for upcoming reminders based on their schedules.
    Creates logs for up to 30 days in the future, respecting schedule start/end dates.
    """
    logger.info("Starting generate_upcoming_reminder_logs...")

    today = timezone.localdate()
    future_window_end = today + timedelta(days=30)

    active_reminders = Reminder.objects.filter(is_active=True).select_related('schedule', 'user')

    logger.info(f"Generating logs for {active_reminders.count()} active reminders up to {future_window_end}...")

    for reminder_obj in active_reminders:
        schedule = reminder_obj.schedule
        user = reminder_obj.user

        if not schedule:
            logger.warning(f"Skipping reminder {reminder_obj.id} as it has no associated schedule.")
            continue

        if schedule.end_date and schedule.end_date < today:
            logger.info(f"Skipping reminder {reminder_obj.id} as its end date ({schedule.end_date}) is in the past.")
            continue

        generation_start_date = max(today, schedule.start_date)
        generation_end_date = min(future_window_end, schedule.end_date or future_window_end)

        if generation_start_date > generation_end_date:
            logger.info(f"Skipping reminder {reminder_obj.id} as generation window is invalid ({generation_start_date} to {generation_end_date}).")
            continue

        logger.info(f"Generating logs for reminder {reminder_obj.id} ({user.username}) from {generation_start_date} to {generation_end_date}")

        expected_occurrences = _generate_expected_occurrences_for_schedule(
            schedule, generation_start_date, generation_end_date
        )

        logs_created_count = 0
        for occurrence_date in expected_occurrences:
            try:
                log_entry, created = DailyReminderLog.objects.get_or_create(
                    reminder=reminder_obj,
                    due_date=occurrence_date,
                    defaults={
                        'user': user,
                        'due_time': schedule.time_of_day,
                    }
                )
                if created:
                    logs_created_count += 1
                    logger.debug(f"Created log for reminder {reminder_obj.id} on {occurrence_date}")
            except DatabaseError as e:
                logger.error(f"Error creating log for reminder {reminder_obj.id} on {occurrence_date}: {e}", exc_info=True)

        if logs_created_count > 0:
            logger.info(f"Created {logs_created_count} logs for reminder {reminder_obj.id}.")

    logger.info("Log generation complete.")

# --- Helper Function for Schedule Occurrences ---
def _generate_expected_occurrences_for_schedule(schedule, start_date, end_date):
    """
    Yields dates when the schedule should occur between start_date and end_date.

    :param schedule: Schedule object with repeat_type and related fields
    :param start_date: Start date for generating occurrences
    :param end_date: End date for generating occurrences
    :yields: Date objects for valid occurrences
    """
    current_date = start_date
    while current_date <= end_date:
        is_an_occurrence = False
        if schedule.repeat_type == 'daily':
            is_an_occurrence = True
        elif schedule.repeat_type == 'weekly':
            selected_weekdays = [int(day) for day in schedule.weekly_days.split(',') if day]
            if current_date.weekday() in selected_weekdays:
                is_an_occurrence = True
        elif schedule.repeat_type == 'monthly':
            # Assuming monthly_dates stores day numbers (1-31)
            try:
                selected_days_of_month = [int(d) for d in schedule.monthly_dates.split(',') if d]
                if current_date.day in selected_days_of_month:
                    is_an_occurrence = True
            except ValueError as e:
                logger.warning(f"Invalid monthly_dates format for schedule {schedule.id}: {e}")
                continue

        if is_an_occurrence:
            yield current_date
        current_date += timedelta(days=1)

# --- Function 3: Update Missed Reminders ---
def update_reminders():
    """
    Marks pending reminders as missed if they are past their grace period.
    Uses the is_past_grace_period property from DailyReminderLog.
    """
    logger.info("Starting update_missed_reminders...")

    now = timezone.now()
    logs_to_update_pks = []

    # Dynamic cutoff based on maximum grace period
    max_grace_days = 30  # Adjust based on maximum possible grace period
    cutoff_date_start = now.date() - timedelta(days=max_grace_days)
    cutoff_date_end = now.date()

    pending_logs = DailyReminderLog.objects.filter(
        status=DailyReminderLog.STATUS_PENDING,
        due_date__gte=cutoff_date_start,
        due_date__lte=cutoff_date_end
    ).select_related('reminder')

    logger.info(f"Found {pending_logs.count()} pending logs to check.")

    for log in pending_logs:
        if not log.reminder:
            logger.warning(f"Log entry {log.pk} has no associated reminder. Skipping.")
            continue

        if log.is_past_grace_period:
            logs_to_update_pks.append(log.pk)
            logger.debug(f"Log {log.pk} (Due: {log.due_datetime}) is past grace period.")

    if logs_to_update_pks:
        try:
            updated_count = DailyReminderLog.objects.filter(pk__in=logs_to_update_pks).update(
                status=DailyReminderLog.STATUS_MISSED
            )
            logger.info(f"Marked {updated_count} reminders as missed.")
        except DatabaseError as e:
            logger.error(f"Database error updating reminders: {e}", exc_info=True)
    else:
        logger.info("No pending reminders found past their grace period.")

    logger.info("Finished update_missed_reminders job.")

# --- Function 4: Check and Notify Streaks ---
def check_and_notify_streaks():
    """
    Checks for users who have achieved a streak that is a multiple of 7 days (e.g., 7, 14, 21)
    and sends a congratulatory email with bonus points information.
    """
    now = timezone.now()
    logger.info(f"[{now.isoformat()}] Starting streak notification check...")

    for user in User.objects.filter(is_active=True):
        try:
            current_streak = calculate_current_adherence_streak(user)
            if current_streak >= 7 and current_streak % 7 == 0:
                user_stats, _ = UserStats.objects.get_or_create(user=user)
                if user_stats.last_streak_notification_date != now.date():
                    context = {
                        'user': user,
                        'streak_count': current_streak,
                        'bonus_points': 100,
                        'boost_url': f"{settings.SITE_URL}{reverse('medminder:dashboard')}"
                    }
                    send_email_template(
                        subject=f"🎉 Incredible! You've reached a {current_streak}-day streak!",
                        template_name="template_7day_streak",
                        context=context,
                        recipient=user.email
                    )
                    user_stats.last_streak_notification_date = now.date()
                    user_stats.save(update_fields=['last_streak_notification_date'])
                    logger.info(f"Sent streak notification to {user.email}")
        except Exception as e:
            logger.error(f"Error processing streak for {user.email}: {e}", exc_info=True)

    logger.info("Finished streak notification check.")

# --- Function 5: Check and Notify Lost Streaks ---
def check_and_notify_lost_streaks():
    """
    Checks for users who have lost a streak of 3 or more days and sends an
    encouragement email to get back on track.
    """
    now = timezone.now()
    logger.info(f"[{now.isoformat()}] Starting lost streak notification check...")

    for user in User.objects.filter(is_active=True):
        try:
            user_stats, _ = UserStats.objects.get_or_create(
                user=user,
                defaults={'date': timezone.now().date()}  # Add default date
            )
            current_streak = calculate_current_adherence_streak(user)
            if user_stats.previous_streak >= 3 and current_streak == 0 and user_stats.last_lost_streak_notification_date != now.date():
                context = {
                    'user': user,
                    'previous_streak': user_stats.previous_streak,
                    'dashboard_url': f"{settings.SITE_URL}{reverse('medminder:dashboard')}"
                }
                send_email_template(
                    subject="Don't Give Up - Your MedMinder Streak",
                    template_name="template_lost_streak",
                    context=context,
                    recipient=user.email
                )
                user_stats.last_lost_streak_notification_date = now.date()
                user_stats.save(update_fields=['last_lost_streak_notification_date'])
                logger.info(f"Sent lost streak notification to {user.email}")
        except Exception as e:
            logger.error(f"Error processing lost streak for {user.email}: {e}", exc_info=True)

    logger.info("Finished lost streak notification check.")

# --- Function 6: Check and Notify Inactive Users ---
def check_and_notify_inactive_users(inactivity_days=7):
    """
    Checks for users who haven't logged in for the specified number of days
    and sends a check-in email to encourage them to return.

    :param inactivity_days: Number of days of inactivity to trigger the email (default: 7)
    """
    now = timezone.now()
    logger.info(f"[{now.isoformat()}] Starting inactive user notification check...")

    # Calculate the inactivity threshold
    inactivity_threshold = now - timedelta(days=inactivity_days)

    # Filter active users who haven't logged in recently
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lte=inactivity_threshold
    ).select_related('usersettings')

    logger.info(f"Found {inactive_users.count()} inactive users (last login before {inactivity_threshold.isoformat()}) to check.")

    sent_count = 0
    for user in inactive_users:
        try:
            # Check if user allows email reminders
            try:
                user_settings = user.usersettings
                if not user_settings.receive_email_reminders:
                    logger.info(f"[{now.isoformat()}] User {user.username} has disabled email reminders. Skipping inactivity notification.")
                    continue
            except User.usersettings.RelatedObjectDoesNotExist:
                logger.warning(f"No UserSettings for {user.username}. Assuming emails are allowed.")
                # Proceed with default assumption (can adjust to skip if stricter policy needed)

            # Check if already notified today
            user_stats, _ = UserStats.objects.get_or_create(
                user=user,
                defaults={'date': timezone.now().date()}  # Add default date
            )
            if user_stats.last_inactivity_notification_date == now.date():
                logger.info(f"[{now.isoformat()}] Already sent inactivity notification to {user.email} today. Skipping.")
                continue

            # Prepare email context
            context = {
                'user': user,
                'app_url': f"{settings.SITE_URL}{reverse('medminder:dashboard')}"
            }

            # Send email
            send_email_template(
                subject="MedMinder: We Miss You!",
                template_name="template_come_back",
                context=context,
                recipient=user.email
            )

            # Update notification date
            try:
                user_stats.last_inactivity_notification_date = now.date()
                user_stats.save(update_fields=['last_inactivity_notification_date'])
                sent_count += 1
                logger.info(f"Sent inactivity notification to {user.email}")
            except DatabaseError as e:
                logger.error(f"Failed to update last_inactivity_notification_date for {user.email}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error processing inactivity notification for {user.email}: {e}", exc_info=True)

    logger.info(f"[{now.isoformat()}] Finished inactive user notification check. Sent {sent_count} emails.")