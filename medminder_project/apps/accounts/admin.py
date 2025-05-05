# your_project/apps/accounts/admin.py

from django.contrib import admin
# Import ModelAdmin from unfold instead of django.contrib.admin
from unfold.admin import ModelAdmin

# Import your models from the accounts app
from .models import ReceiveUpdates, Tier, UserSettings

# Import the User model (necessary for autocomplete_fields or raw_id_fields if not default admin)
from django.contrib.auth import get_user_model
User = get_user_model()

# Optional: Customize the default UserAdmin to add search_fields if you want
# to use autocomplete_fields for the User field in UserSettingsAdmin.
# If you already have a custom User admin elsewhere, add search_fields there.
# If not, you can uncomment and use this, or just use raw_id_fields below.
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# @admin.register(User)
# class UserAdmin(BaseUserAdmin, ModelAdmin): # Inherit from BaseUserAdmin and unfold's ModelAdmin
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     # Add other unfold-specific customizations here if needed


@admin.register(Tier)
class TierAdmin(ModelAdmin):
    """Admin configuration for the Tier model."""
    list_display = (
        'name',
        'priority',
        'is_default',
        'max_reminders_display', # Custom method for clarity
        'max_viewers_display',   # Custom method for clarity
        'can_use_sms_reminders',
        # Add other feature limits here
    )
    list_filter = ('is_default', 'can_use_sms_reminders')
    search_fields = ('name', 'description')
    ordering = ('priority',)

    # Needed for autocomplete_fields in UserSettingsAdmin
    search_fields = ('name',) # Add search fields for autocompletion

    # Custom display methods for limits
    def max_reminders_display(self, obj):
        return 'Unlimited' if obj.max_reminders is None else obj.max_reminders
    max_reminders_display.short_description = 'Max Reminders'

    def max_viewers_display(self, obj):
        return 'Unlimited' if obj.max_viewers is None else obj.max_viewers
    max_viewers_display.short_description = 'Max Viewers'


@admin.register(ReceiveUpdates)
class ReceiveUpdatesAdmin(ModelAdmin):
    """Admin configuration for the ReceiveUpdates model (Waitlist)."""
    list_display = ('user', 'email', 'notifications')
    list_filter = ('notifications',)
    search_fields = ('user__username', 'email') # Search by user username or email

    # Since 'user' is a OneToOneField, you can't have multiple ReceiveUpdates per user.
    # autocomplete_fields or raw_id_fields would be for selecting the user when adding/changing.
    # autocomplete_fields = ('user',) # Requires search_fields on UserAdmin
    raw_id_fields = ('user',) # Alternative to autocomplete_fields

    # Readonly fields if they should not be changed manually (e.g., if set programmatically)
    # readonly_fields = ('user',) # Could make user read-only after creation


@admin.register(UserSettings)
class UserSettingsAdmin(ModelAdmin):
    """Admin configuration for the UserSettings model."""
    list_display = (
        'user',
        'account_tier',
        'subscription_status',
        'receive_email_reminders',
        'receive_sms_reminders',
        'payment_customer_id',
        'payment_subscription_id',
        'subscription_end_date',
        # Add other settings here
    )
    list_filter = (
        'account_tier',
        'subscription_status',
        'receive_email_reminders',
        'receive_sms_reminders',
    )
    search_fields = (
        'user__username', # Search by related user's username
        'user__email',    # Search by related user's email
        'payment_customer_id',
        'payment_subscription_id',
    )

    # Use autocomplete_fields for a better user experience with many users/tiers.
    # REQUIRES search_fields to be defined in the admin class of the related model (User and Tier).
    # Uncomment the UserAdmin customization above or ensure your existing User admin has search_fields.
    autocomplete_fields = ('user', 'account_tier')

    # OR use raw_id_fields as a simpler alternative if autocomplete is not working or desired
    # raw_id_fields = ('user', 'account_tier')

    # Fields that should not be manually edited in the admin, managed by code/payment gateway
    # You might make avatar_bg_color and avatar_text_color readonly if only set by the signal
    readonly_fields = (
        'payment_customer_id',
        'payment_subscription_id',
        'subscription_end_date',
        'avatar_bg_color', # Make readonly if only set by signal
        'avatar_text_color', # Make readonly if only set by signal
    )

    # Optional: Fieldsets to group fields in the add/change form
    # fieldsets = (
    #     (None, {
    #         'fields': ('user', 'account_tier', 'subscription_status')
    #     }),
    #     ('Notification Preferences', {
    #         'fields': ('receive_email_reminders', 'receive_sms_reminders')
    #     }),
    #     ('Payment Gateway Info', {
    #         'fields': ('payment_customer_id', 'payment_subscription_id', 'subscription_end_date'),
    #         'classes': ('collapse',), # Optional: make this section collapsible
    #     }),
    #     ('Avatar Colors', {
    #         'fields': ('avatar_bg_color', 'avatar_text_color'),
    #         'classes': ('collapse',),
    #     }),
    # )


# Note: The signal `create_user_settings` is defined in your models.py,
# which is perfectly fine. You don't need to put signals in admin.py.