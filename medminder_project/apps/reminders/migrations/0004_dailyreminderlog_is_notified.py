# Generated by Django 5.2 on 2025-04-21 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "reminders",
            "0003_remove_reminder_completed_remove_reminder_due_date_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyreminderlog",
            name="is_notified",
            field=models.BooleanField(default=False),
        ),
    ]
