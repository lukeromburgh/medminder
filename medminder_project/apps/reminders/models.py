from datetime import timedelta, datetime
# import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Correct import

class Medication(models.Model):
    medication_name = models.CharField(max_length=255, verbose_name='Medication Name')

    def __str__(self):
        return self.medication_name

class Dosage(models.Model):
    dosage = models.CharField(max_length=255, verbose_name='Dosage')

    def __str__(self):
        return self.dosage

class Schedule(models.Model):
    REPEAT_CHOICES = [
        ('', 'Never'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        
    ]
    repeat_type = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='')
    # For weekly: comma-separated integers (0=Mon, 6=Sun)
    weekly_days = models.CharField(max_length=20, blank=True, null=True)
    # For monthly: comma-separated integers (1-31)
    monthly_dates = models.CharField(max_length=100, blank=True, null=True)
    # Time of day for the reminder
    time_of_day = models.TimeField(default=timezone.now)
    # When the recurring plan starts
    start_date = models.DateField(default=timezone.now)
    # Optional end date for the recurring plan
    end_date = models.DateField(blank=True, null=True)
    # Add an interval? e.g., every 2 days, every 3 weeks
    # repeat_interval = models.PositiveIntegerField(default=1)


    def __str__(self):
        # Basic representation, you can make this more detailed
        if self.repeat_type == 'daily':
            return f"Daily at {self.time_of_day}"
        elif self.repeat_type == 'weekly':
             days = self.weekly_days.split(',') if self.weekly_days else []
             day_names = [dict(self.day_choices()).get(int(d)) for d in days]
             return f"Weekly on {', '.join(day_names or ['No days selected'])} at {self.time_of_day}"
        # ... add logic for monthly/yearly
        return f"{self.repeat_type.capitalize()} schedule"

    # Helper for weekly day names (optional, could be in form too)
    def day_choices(self):
         # This should match your form's DAYS_OF_WEEK
         return [(0, 'Mon'), (1, 'Tue'), (2, 'Wed'), (3, 'Thu'), (4, 'Fri'), (5, 'Sat'), (6, 'Sun')]


class Reminder(models.Model):
    # id is automatically added by Django
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Use settings.AUTH_USER_MODEL
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.ForeignKey(Dosage, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    grace_period = models.DurationField(
         default=timedelta(minutes=15),
         help_text="Grace period after due time before marking as missed (e.g., 15 minutes)."
    )
    # Fields like due_date, due_time, completed are NOT here, they are on the log
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # To easily pause/resume a plan

    def __str__(self):
        return f"Plan for {self.user.username}: {self.medication} - {self.dosage} ({self.schedule})"

# DailyReminderLog represents a specific occurrence of a reminder on a given day
class DailyReminderLog(models.Model):
    reminder = models.ForeignKey('Reminder', on_delete=models.CASCADE, related_name='logs') # Use string 'Reminder' if defined later in file
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    due_date = models.DateField(db_index=True)
    due_time = models.TimeField()
    is_notified = models.BooleanField(default=False) # For tracking push/email notifications

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_SKIPPED = 'skipped'
    STATUS_MISSED = 'missed'
    STATUS_TAKEN_LATE = 'taken_late'
    # STATUS_SNOOZED = 'snoozed' # Uncomment if snooze feature is added

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),      # Due, but not yet actioned or missed
        (STATUS_COMPLETED, 'Completed'),  # Actioned by user within grace period
        (STATUS_SKIPPED, 'Skipped'),      # Actioned by user as skipped
        (STATUS_MISSED, 'Missed'),        # Past due time + grace period, not actioned
        (STATUS_TAKEN_LATE, 'Taken Late'),# Actioned by user after grace period
        # (STATUS_SNOOZED, 'Snoozed'),
    ]
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    # Renamed for clarity, stores when the *action* (complete/skip) was taken
    action_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the reminder was marked completed, skipped, or taken late."
    )

    class Meta:
        unique_together = ('reminder', 'due_date')
        ordering = ['due_date', 'due_time']
        indexes = [
            models.Index(fields=['due_date', 'status']), # Index for filtering by date and status
        ]

    def __str__(self):
        # Use status display name for readability
        return f"Log for {self.reminder.medication} ({self.user.username}) on {self.due_date} at {self.due_time}: {self.get_status_display()}"

    @property
    def due_datetime(self):
        """Combines due_date and due_time into a timezone-aware datetime."""
        # Combine date and time using the imported datetime *class*
        naive_datetime = datetime.combine(self.due_date, self.due_time)
        # Make it timezone-aware using Django's current timezone
        # Assumes settings.USE_TZ = True and settings.TIME_ZONE is set
        # For user-specific timezones, you might need to fetch the user's profile timezone
        current_tz = timezone.get_current_timezone()
        return timezone.make_aware(naive_datetime, current_tz)

    @property
    def is_past_due(self):
        """Checks if the current time is past the due_datetime."""
        return timezone.now() > self.due_datetime

    @property
    def is_past_grace_period(self):
        """Checks if the current time is past the due_datetime + grace period."""
        # Ensure timedelta is imported from datetime
        grace_period = getattr(self.reminder, 'grace_period', timedelta(minutes=15)) # Default grace if not on reminder
        return timezone.now() > (self.due_datetime + grace_period)

    @property
    def effective_status(self):
        """
        Calculates the status based on the current time,
        useful for display even if the DB status hasn't been updated by a cron job.
        """
        # If already actioned, return the stored status
        if self.status != self.STATUS_PENDING:
            return self.status

        # If pending, check if it should now be considered missed
        if self.is_past_grace_period:
            return self.STATUS_MISSED
        else:
            # Still pending and within grace period (or not yet due)
            return self.STATUS_PENDING

    def mark_complete(self):
        """Sets status to completed or taken_late based on current time."""
        now = timezone.now()
        self.action_timestamp = now

        if self.is_past_grace_period:
             # Marked complete *after* the grace period ended
            self.status = self.STATUS_TAKEN_LATE
        else:
            # Marked complete within the allowed time / grace period
            self.status = self.STATUS_COMPLETED

        self.save(update_fields=['status', 'action_timestamp'])

    # --- Example: Method to call from your 'Skip' view ---
    def mark_skipped(self):
        """Sets status to skipped."""
        self.status = self.STATUS_SKIPPED
        self.action_timestamp = timezone.now() # Record when skipped
        self.save(update_fields=['status', 'action_timestamp'])



class Viewer(models.Model):
    viewer_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewed_user')
    viewer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewer')
    access_granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.viewer_user.username} viewing {self.user.username}"

class UserStats(models.Model):
    stat_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    reminders_completed = models.IntegerField(default=0)
    reminders_skipped = models.IntegerField(default=0)
    average_compliance = models.FloatField(default=0.0)
    other_stats = models.JSONField(null=True, blank=True)
    achievement_points = models.IntegerField(default=0)  # Add achievement_points field
    last_streak_notification_date = models.DateField(null=True, blank=True)
    last_lost_streak_notification_date = models.DateField(null=True, blank=True)
    previous_streak = models.IntegerField(default=0)
    last_inactivity_notification_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} stats - {self.date}"

class ReminderStats(models.Model):
    reminder_stat_id = models.AutoField(primary_key=True)
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    completion_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reminder.medication_name} stats - {self.date}"