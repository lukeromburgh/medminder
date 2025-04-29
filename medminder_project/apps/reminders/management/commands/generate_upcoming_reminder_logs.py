# reminders/management/commands/generate_upcoming_reminder_logs.py

import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from ...models import Reminder, DailyReminderLog
# You might need to import your Schedule model if generation logic is there
# from ...models import Schedule

class Command(BaseCommand):
    help = 'Generates DailyReminderLog entries for upcoming reminders.'

    def handle(self, *args, **options):
        # Define the window for which to generate logs (e.g., next 30 days)
        today = date.today()
        future_window_end = today + timedelta(days=30)

        # Fetch active reminders
        active_reminders = Reminder.objects.filter(is_active=True)

        self.stdout.write(self.style.SUCCESS(f'Starting log generation for active reminders up to {future_window_end}...'))

        for reminder in active_reminders:
            schedule = reminder.schedule # Get the linked schedule

            # Check if the reminder plan has ended
            if schedule.end_date and schedule.end_date < today:
                 # Optionally deactivate the reminder if its end date is past
                 # reminder.is_active = False
                 # reminder.save()
                 self.stdout.write(f'Skipping reminder {reminder.id} as its end date ({schedule.end_date}) is in the past.')
                 continue

            # Determine the date range to consider for this reminder
            # Start from today or the schedule start date if it's in the future
            generation_start_date = max(today, schedule.start_date)
            # End at the future window end or the schedule end date, whichever is sooner
            generation_end_date = future_window_end
            if schedule.end_date and schedule.end_date < generation_end_date:
                 generation_end_date = schedule.end_date


            if generation_start_date > generation_end_date:
                 self.stdout.write(f'Skipping reminder {reminder.id} as generation window is invalid ({generation_start_date} to {generation_end_date}).')
                 continue


            self.stdout.write(f'Generating logs for reminder {reminder.id} from {generation_start_date} to {generation_end_date}')

            # --- Logic to Generate Expected Occurrences ---
            # This is the core part. You need a function/method that takes
            # the schedule and date range and yields occurrence dates.

            expected_occurrences = self.generate_expected_occurrences(schedule, generation_start_date, generation_end_date)

            # --- Create DailyReminderLog entries using get_or_create ---
            for occurrence_date in expected_occurrences:
                 # Use get_or_create to avoid duplicates
                 log_entry, created = DailyReminderLog.objects.get_or_create(
                     reminder=reminder,
                     due_date=occurrence_date,
                     defaults={
                         'user': reminder.user, # Denormalized user
                         'due_time': schedule.time_of_day # Use time from schedule
                         # status will default to 'pending'
                     }
                 )
                 if created:
                     self.stdout.write(f'  Created log for {reminder.id} on {occurrence_date}')
                 # else: log_entry already existed

        self.stdout.write(self.style.SUCCESS('Log generation complete.'))


    def generate_expected_occurrences(self, schedule, start_date, end_date):
        """
        Helper function to calculate expected occurrence dates based on schedule rules.
        Yields date objects.
        """
        current_date = start_date
        # Iterate through the date range
        while current_date <= end_date:
            is_an_occurrence = False

            if schedule.repeat_type == 'daily':
                is_an_occurrence = True
            elif schedule.repeat_type == 'weekly':
                # current_date.weekday() returns 0-6 (Mon-Sun)
                # weekly_days stores comma-separated integers '0,2,4' etc.
                selected_weekdays = [int(day) for day in schedule.weekly_days.split(',') if day]
                if current_date.weekday() in selected_weekdays:
                    is_an_occurrence = True
            elif schedule.repeat_type == 'monthly':
                # monthly_dates stores comma-separated YYYY-MM-DD strings from Flatpickr
                # We need the day of the month
                selected_days_of_month = [datetime.date.fromisoformat(d).day for d in schedule.monthly_dates.split(',') if d]
                if current_date.day in selected_days_of_month:
                    is_an_occurrence = True
            # TODO: Add logic for yearly

            # Also check against the schedule's end date
            if schedule.end_date and current_date > schedule.end_date:
                 is_an_occurrence = False # Should already be handled by loop bounds, but good failsafe

            if is_an_occurrence:
                yield current_date # Yield the date of the occurrence

            current_date += timedelta(days=1) # Move to the next day