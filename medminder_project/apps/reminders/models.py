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
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, verbose_name='Repeat')
    at_time = models.TimeField(verbose_name='At')
    until_date = models.DateField(null=True, blank=True, verbose_name='Until')

    def __str__(self):
        return f"{self.repeat} at {self.at_time}"

class Reminder(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Removed default argument
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.ForeignKey(Dosage, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    due_date = models.DateField()
    due_time = models.TimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.medication} - {self.dosage} - {self.schedule} - Due: {self.due_date} {self.due_time}"

    def save(self, *args, **kwargs):
        """Override save to calculate due_date and due_time."""
        if not self.id:  # Only calculate on creation
            today = timezone.now().date()
            self.due_date = today
            self.due_time = self.schedule.at_time
        super().save(*args, **kwargs)

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