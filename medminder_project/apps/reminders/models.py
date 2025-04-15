from django.db import models

class Medication(models.Model):
    medication_name = models.CharField(max_length=255, verbose_name='Medication Name')  # Added max_length

    def __str__(self):
        return self.medication_name

class Dosage(models.Model):
    dosage = models.CharField(max_length=255, verbose_name='Dosage') #Added max_length

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
    until_date = models.DateField(null=True, blank=True, verbose_name='Until')  # Made it nullable

    def __str__(self):
        return f"{self.repeat} at {self.at_time}"

from django.db import models
from django.contrib.auth.models import User  # Import the User model

class Reminder(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.ForeignKey(Dosage, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    def get_default_user():
        return User.objects.get_or_create(username='default_reminder_user')[0].id

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.medication} - {self.dosage} - {self.schedule}"
