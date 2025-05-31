# apps/reminders/management/commands/update_missed_reminders.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
# Assuming your models are in apps.reminders.models
from apps.reminders.models import DailyReminderLog, Reminder

class Command(BaseCommand):
    help = 'Finds pending reminders that are past their grace period and marks them as missed.'

    # You can add arguments here if needed, e.g., to specify a user
    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        The main logic of the command.
        """
        self.stdout.write(self.style.SUCCESS('Starting update_missed_reminders command...'))

        now = timezone.now()
        logs_to_update_pks = [] # Collect primary keys for bulk update

        # Define a reasonable cutoff date for efficiency
        # Only check logs from the last 7 days to avoid processing old data unnecessarily
        cutoff_date = now.date() - timedelta(days=7)

        # Iterate over reminders to access grace_period efficiently
        # Filtering reminders first can be more efficient than filtering logs directly
        # if you have many logs per reminder but fewer reminders.
        # Adjust filtering based on performance needs and data volume.
        # .select_related('reminder') can be used if accessing reminder fields within the loop
        # but prefetch_related('logs') is good if you're iterating through reminder.logs
        reminders = Reminder.objects.all() # Or filter users, etc.

        self.stdout.write(f"Checking {reminders.count()} reminders...")

        for reminder in reminders:
            # Ensure reminder has a grace_period attribute or handle its absence
            # Using getattr with a default is safer if grace_period might not exist
            grace_period = getattr(reminder, 'grace_period', timedelta(minutes=60))

            # Filter pending logs for this specific reminder within the cutoff date
            # Using .filter(reminder=reminder) is efficient here
            pending_logs = DailyReminderLog.objects.filter(
                reminder=reminder,
                status=DailyReminderLog.STATUS_PENDING,
                due_date__gte=cutoff_date
            )

            # Check each pending log if it's past its grace period
            for log in pending_logs:
                # Use the due_datetime property which handles timezone conversion
                due_datetime_aware = log.due_datetime

                # Check if the current time is past the due time plus the grace period
                if now > (due_datetime_aware + grace_period):
                    logs_to_update_pks.append(log.pk) # Add the primary key to the list

        # Perform a bulk update if there are logs to mark as missed
        if logs_to_update_pks:
            updated_count = DailyReminderLog.objects.filter(pk__in=logs_to_update_pks).update(
                status=DailyReminderLog.STATUS_MISSED
            )
            message = f"Successfully marked {updated_count} reminders as missed."
            self.stdout.write(self.style.SUCCESS(message))
            return message # Return message for testing/external use
        else:
            message = "No pending reminders found past grace period."
            self.stdout.write(self.style.SUCCESS(message))
            return message # Return message

        self.stdout.write(self.style.SUCCESS('Finished update_missed_reminders command.'))

