from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from django.contrib.auth import get_user_model
from .models import ReminderStats, UserStats, Reminder, DailyReminderLog

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_stats(sender, instance, created, **kwargs):
    if created:
        UserStats.objects.create(
            user=instance,
            date=now().date(),
        )

@receiver(post_save, sender=Reminder)
def create_reminder_stats(sender, instance, created, **kwargs):
    """
    Creates or updates ReminderStats when a Reminder is created or updated.
    """
    if created:
        # Create a ReminderStats entry when a Reminder is created
        ReminderStats.objects.create(reminder=instance, date=timezone.now().date())
    else:
        # Update ReminderStats if the Reminder is updated
        try:
            reminder_stats = ReminderStats.objects.get(reminder=instance, date=timezone.now().date())
        except ReminderStats.DoesNotExist:
            # Create a ReminderStats entry if it doesn't exist
             reminder_stats = ReminderStats.objects.create(reminder=instance, date=timezone.now().date())

        # Logic to determine if the reminder was completed
        # This depends on how you track completion (e.g., DailyReminderLog)
        # Example (adjust based on your actual logic):
        completed = DailyReminderLog.objects.filter(reminder=instance, due_date=timezone.now().date(), status='completed').exists()
        reminder_stats.completed = completed
        reminder_stats.save()

@receiver(post_save, sender=DailyReminderLog)
def update_reminder_stats_on_log_completion(sender, instance, **kwargs):
    """
    Updates ReminderStats when a DailyReminderLog entry is marked as completed.
    """
    if instance.status == 'completed':
        try:
            reminder_stats = ReminderStats.objects.get(reminder=instance.reminder, date=instance.due_date)
            reminder_stats.completed = True
            reminder_stats.save()
        except ReminderStats.DoesNotExist:
            # Create a ReminderStats entry if it doesn't exist
            ReminderStats.objects.create(reminder=instance.reminder, date=instance.due_date, completed=True)
