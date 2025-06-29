# your_project/apps/reminders/admin.py

from django.contrib import admin
from django.db import (
    models,
)  # Import models for formfield_for_foreignkey if needed (unlikely with autocomplete)
from django.forms import Textarea  # Import Textarea if needed for formfield_overrides
from django.utils.html import format_html  # For rendering HTML in list_display

# Import ModelAdmin from unfold instead of django.contrib.admin
from unfold.admin import ModelAdmin

# Import your models from the reminders app
from .models import (
    Medication,
    Dosage,
    Schedule,
    Reminder,
    DailyReminderLog,
    Viewer,
    UserStats,
    ReminderStats,
)

# Assuming accounts.models.User is your AUTH_USER_MODEL
# You might need to explicitly import or reference it if not the default Django User
# from your_project.apps.accounts.models import UserSettings # Example if needed for autocomplete


@admin.register(Medication)
class MedicationAdmin(ModelAdmin):
    """Admin configuration for the Medication model."""

    list_display = ("medication_name",)
    search_fields = ("medication_name",)
    # You might want to order them alphabetically
    ordering = ("medication_name",)


@admin.register(Dosage)
class DosageAdmin(ModelAdmin):
    """Admin configuration for the Dosage model."""

    list_display = ("dosage",)
    search_fields = ("dosage",)
    ordering = ("dosage",)


@admin.register(Schedule)
class ScheduleAdmin(ModelAdmin):
    """Admin configuration for the Schedule model."""

    list_display = (
        "repeat_type",
        "time_of_day",
        "start_date",
        "end_date_display",
        "weekly_days",
        "monthly_dates",
    )
    list_filter = ("repeat_type",)
    search_fields = ("weekly_days", "monthly_dates")  # Can search text fields
    date_hierarchy = "start_date"  # Adds date drill-down navigation

    # Add a method to display end_date nicely, handling None
    def end_date_display(self, obj):
        return obj.end_date if obj.end_date else "Never"

    end_date_display.short_description = "End Date"  # Column header

    # Optional: Configure form fields if needed, e.g., for Textarea
    # formfield_overrides = {
    #     models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    # }


@admin.register(Reminder)
class ReminderAdmin(ModelAdmin):
    """Admin configuration for the Reminder model."""

    list_display = (
        "user",
        "medication",
        "dosage",
        "schedule",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "medication", "dosage", "schedule")
    search_fields = (
        "user__username",  # Search by related user's username
        "medication__medication_name",  # Search by related medication name
        "dosage__dosage",  # Search by related dosage text
    )
    raw_id_fields = (
        "user",
        "medication",
        "dosage",
        "schedule",
    )  # Good for performance with many related objects
    # OR use autocomplete_fields if you have search views configured for related models:
    # autocomplete_fields = ('user', 'medication', 'dosage', 'schedule')
    # Note: For autocomplete_fields, you need search_fields defined in the related model's admin class
    # (e.g., search_fields on UserAdmin, MedicationAdmin, etc.)
    readonly_fields = ("created_at",)


@admin.register(DailyReminderLog)
class DailyReminderLogAdmin(ModelAdmin):
    """Admin configuration for the DailyReminderLog model."""

    list_display = (
        "user",
        "due_date",
        "due_time",
        "medication_name",  # Custom method display
        "dosage_display",  # Custom method display
        "status",
        "effective_status_display",  # Custom method display
        "is_notified",
        "action_timestamp",
    )
    list_filter = (
        "status",
        "is_notified",
        "due_date",
        "reminder__medication",  # Filter by related reminder's medication
        "user",
    )
    search_fields = (
        "user__username",
        "reminder__medication__medication_name",
        "reminder__dosage__dosage",
    )
    date_hierarchy = "due_date"
    raw_id_fields = (
        "reminder",
        "user",
    )  # Or use autocomplete_fields = ('reminder', 'user') if configured
    readonly_fields = ("action_timestamp",)  # action_timestamp is set programmatically

    # --- Custom list_display methods ---
    def medication_name(self, obj):
        return obj.reminder.medication.medication_name

    medication_name.short_description = "Medication"
    medication_name.admin_order_field = (
        "reminder__medication__medication_name"  # Allows sorting
    )

    def dosage_display(self, obj):
        return obj.reminder.dosage.dosage

    dosage_display.short_description = "Dosage"
    dosage_display.admin_order_field = "reminder__dosage__dosage"  # Allows sorting

    def effective_status_display(self, obj):
        """Displays the effective status with color coding."""
        effective_stat = obj.effective_status
        color = (
            "green"
            if effective_stat in [obj.STATUS_COMPLETED, obj.STATUS_TAKEN_LATE]
            else ("red" if effective_stat == obj.STATUS_MISSED else "orange")
        )
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_effective_status_display(),
        )

    effective_status_display.short_description = "Effective Status"
    # Cannot easily order by a computed property like effective_status

    # --- End Custom list_display methods ---


@admin.register(Viewer)
class ViewerAdmin(ModelAdmin):
    """Admin configuration for the Viewer model."""

    list_display = ("user", "viewer_user", "access_granted_at")
    list_filter = ("access_granted_at", "user", "viewer_user")
    raw_id_fields = ("user", "viewer_user")  # Or use autocomplete_fields
    readonly_fields = ("access_granted_at",)
    search_fields = ("user__username", "viewer_user__username")


@admin.register(UserStats)
class UserStatsAdmin(ModelAdmin):
    """Admin configuration for the UserStats model."""

    list_display = (
        "user",
        "date",
        "reminders_completed",
        "reminders_skipped",
        "average_compliance",
        "achievement_points",
    )
    list_filter = ("date", "user")
    date_hierarchy = "date"
    raw_id_fields = ("user",)  # Or use autocomplete_fields
    search_fields = ("user__username",)
    ordering = ("-date", "user__username")  # Order by latest date first

    # If 'other_stats' JSONField needs specific form handling
    # formfield_overrides = {
    #     models.JSONField: {'widget': Textarea(attrs={'rows': 5, 'cols': 80})},
    # }


@admin.register(ReminderStats)
class ReminderStatsAdmin(ModelAdmin):
    """Admin configuration for the ReminderStats model."""

    list_display = ("reminder", "date", "completed", "skipped", "completion_time")
    list_filter = (
        "date",
        "completed",
        "skipped",
        "reminder__medication",
        "reminder__user",
    )  # Filter by related fields
    date_hierarchy = "date"
    raw_id_fields = ("reminder",)  # Or use autocomplete_fields
    search_fields = (
        "reminder__medication__medication_name",
        "reminder__user__username",
    )
    ordering = ("-date", "reminder")  # Order by latest date first
