from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from django.contrib.auth import get_user_model
from .models import ReminderStats, UserStats, Reminder, DailyReminderLog

User = get_user_model()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_stats(sender, instance, created, **kwargs):
    """
    Creates a UserStats object automatically when a new user is created.
    """
    # The 'instance' received by the signal is the actual user object,
    # so you don't need get_user_model() inside the function either.
    if created:
        # You will need the UserStats model imported here or within the function if preferred,
        # but importing at the module level is standard if it's just for use in signals.
        # from .models import UserStats # Could import here instead if needed

        UserStats.objects.create(
            user=instance, # 'instance' is the newly created User object
            date=timezone.now().date(),
            # Other fields will take their default values
        )
        # Optional: Add a print statement here for debugging if needed
        # print(f"UserStats created for {instance.username}")



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
