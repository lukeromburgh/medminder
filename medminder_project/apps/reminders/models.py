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
    # Fields like due_date, due_time, completed are NOT here, they are on the log
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # To easily pause/resume a plan

    def __str__(self):
        return f"Plan for {self.user.username}: {self.medication} - {self.dosage} ({self.schedule})"

# DailyReminderLog represents a specific occurrence of a reminder on a given day
class DailyReminderLog(models.Model):
    # log_id is automatically added by Django
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Denormalize user for easier querying
    due_date = models.DateField(db_index=True) # The date this log applies to
    due_time = models.TimeField() # The time it was due on that date
    is_notified = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        # Add 'snoozed' or other states if needed
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True)

    completion_timestamp = models.DateTimeField(null=True, blank=True) # When it was marked completed/skipped

    class Meta:
        # Ensure only one log entry per reminder plan per date
        unique_together = ('reminder', 'due_date')
        # Order by due date and time by default for listings
        ordering = ['due_date', 'due_time']

    def __str__(self):
        # More informative string representation
        return f"Log for {self.reminder.medication} ({self.reminder.user.username}) on {self.due_date} at {self.due_time}: {self.status}"


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