# Generated by Django 5.2 on 2025-05-20 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reminders", "0006_userstats_last_lost_streak_notification_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userstats",
            name="last_inactivity_notification_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
