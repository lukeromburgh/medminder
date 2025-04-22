from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from apps.reminders.models import DailyReminderLog, ReminderStats, Reminder  # Import Reminder
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates or updates ReminderStats based on the previous day\'s DailyReminderLog entries.'

    def handle(self, *args, **options):
        yesterday = timezone.now().date() - timedelta(days=1)
        user_ids = DailyReminderLog.objects.values_list('user_id', flat=True).distinct()  # Use user_id

        for user_id in user_ids:
            completed_yesterday = DailyReminderLog.objects.filter(
                user_id=user_id,
                due_date=yesterday,
                status='completed'
            ).exists()

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {user_id} not found.'))
                continue

            # Filter ReminderStats based on reminders belonging to the user
            ReminderStats.objects.update_or_create(
                reminder__user=user,  # Access user through the reminder ForeignKey
                date=yesterday,
                defaults={'completed': completed_yesterday}
            )

            if completed_yesterday:
                self.stdout.write(self.style.SUCCESS(f'ReminderStats updated for user {user_id} on {yesterday}: Completed'))
            else:
                self.stdout.write(self.style.SUCCESS(f'ReminderStats updated for user {user_id} on {yesterday}: Not Completed'))

        self.stdout.write(self.style.SUCCESS('Successfully populated/updated ReminderStats.'))