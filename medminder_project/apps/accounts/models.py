import random
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

# Optional: Model to define the different tiers (e.g., Free, Pro, Premium)
# Recommended if you have multiple tiers or need to store tier-specific features/limits
class Tier(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., 'Free', 'Pro', 'Premium'
    description = models.TextField(blank=True) # Describe the tier's benefits
    priority = models.IntegerField(default=0, help_text="Lower number means higher priority/better tier") # Optional: for ordering tiers
    is_default = models.BooleanField(default=False, help_text="Designates if this is the default tier for new users.")

    # Add tier-specific feature limits here
    max_reminders = models.IntegerField(default=None, null=True, blank=True, help_text="Maximum number of active reminders allowed (-1 or None for unlimited)")
    max_viewers = models.IntegerField(default=None, null=True, blank=True, help_text="Maximum number of viewers allowed (-1 or None for unlimited)")
    can_use_sms_reminders = models.BooleanField(default=False)
    # Add other limits/features as needed

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name

# User Settings model, now including tier and subscription info
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usersettings') # Use related_name for easy access from User
    receive_email_reminders = models.BooleanField(default=True) # Keep existing setting
    receive_sms_reminders = models.BooleanField(default=False) # Keep existing setting
    avatar_bg_color = models.CharField(max_length=50, default='bg-gray-200', help_text="Background color for the user's avatar.")
    avatar_text_color = models.CharField(max_length=50, default='text-gray-800', help_text="Text color for the user's avatar.")
    # Fields for payment/tier integration:

    # Link to the user's account tier.
    # If a Tier model exists, link to it. If not, you could use a CharField like 'account_tier'
    account_tier = models.ForeignKey(
        Tier,
        on_delete=models.SET_NULL, # Set to NULL if a tier is deleted
        null=True,
        blank=True,
        help_text="The user's current subscription tier."
    )

    # Fields related to subscription status from the payment gateway
    # Common statuses: 'trialing', 'active', 'past_due', 'canceled', 'unpaid'
    subscription_status = models.CharField(
        max_length=50,
        default='free', # Default status for users not on a paid plan
        help_text="Current status of the user's subscription."
    )
    payment_customer_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True, # Payment gateway customer ID should be unique
        help_text="Customer ID from the payment gateway (e.g., Stripe Customer ID)."
    )
    payment_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True, # Subscription ID should be unique
        help_text="Subscription ID from the payment gateway."
    )
    subscription_end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the current subscription period ends."
    )

    # Add other settings here as needed

    def is_on_paid_plan(self):
        """Helper method to check if the user is currently on an active paid plan."""
        # Assuming 'active' and 'trialing' are statuses for paid plans
        # And 'free' is the status for non-paying users
        return self.subscription_status in ['trialing', 'active']

    def get_effective_tier(self):
        """Gets the user's tier object, falling back to a default 'Free' tier if needed."""
        # This method is useful if you always need a Tier object to check limits
        if self.account_tier:
            return self.account_tier
        # Fallback to a default 'Free' tier if the user somehow has no tier assigned
        # Ensure you have a Tier object in your DB marked as is_default=True
        try:
            return Tier.objects.get(is_default=True)
        except Tier.DoesNotExist:
            # Handle case where no default tier is defined (shouldn't happen in production)
            # Maybe return a minimal default Tier object or raise an error
            # For simplicity, let's assume a default always exists or return None
            return None # Or raise an error/return a default object


    class Meta:
        verbose_name_plural = "User Settings" # Nicer name in Admin

    def __str__(self):
        tier_name = self.account_tier.name if self.account_tier else 'No Tier'
        return f"Settings for {self.user.username} ({tier_name})"

# Signal to automatically create UserSettings for new Users
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        # Find the default tier (make sure one Tier object has is_default=True)
        default_tier = None
        try:
            default_tier = Tier.objects.get(is_default=True)
        except Tier.DoesNotExist:
            # Handle the case where no default tier exists (e.g., log a warning)
            print("WARNING: No default Tier found. Please create one in the admin.")
            pass # UserSettings will be created without a tier, needs manual assignment

        # Create UserSettings for the new user
        avatar_colors = ProfileColor() # Call the function to get random colors
        bg_color, text_color = avatar_colors # Unpack the tuple

        UserSettings.objects.create(user=instance, account_tier=default_tier, subscription_status='free', avatar_bg_color=bg_color, avatar_text_color=text_color) # Assign default tier and status on creation

# Note: The save_user_settings signal is not strictly needed for OneToOne fields
# when accessing from the User instance like instance.usersettings.save()
# @receiver(post_save, sender=User)
# def save_user_settings(sender, instance, **kwargs):
#     # This signal is more complex for OneToOne relationships managed via related_name
#     # The create signal above is sufficient for initial creation.
#     pass

def ProfileColor():

    colors = [
    ('bg-red-200', 'text-red-800'),
    ('bg-blue-200', 'text-blue-800'),
    ('bg-green-200', 'text-green-800'),
    ('bg-yellow-200', 'text-yellow-800'),
    ('bg-purple-200', 'text-purple-800'),
    ('bg-pink-200', 'text-pink-800'),
    ('bg-indigo-200', 'text-indigo-800'),
    ('bg-teal-200', 'text-teal-800'),
    ('bg-orange-200', 'text-orange-800'),
    ('bg-gray-200', 'text-gray-800'), 
    ('bg-emerald-200', 'text-emerald-800'),
    ('bg-lime-200', 'text-lime-800'),
    ('bg-cyan-200', 'text-cyan-800'),
    ('bg-sky-200', 'text-sky-800'),
    ('bg-fuchsia-200', 'text-fuchsia-800'),
    ('bg-violet-200', 'text-violet-800'),
    ('bg-rose-200', 'text-rose-800'),
    ('bg-zinc-200', 'text-zinc-800'),
    ('bg-neutral-200', 'text-neutral-800')
    ]

    return random.choice(colors)

class ReceiveUpdates(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='waitlist')
    email = models.EmailField(max_length=255, unique=True)
    notifications = models.BooleanField(default=True, help_text="Receive notifications about updates and new features.")

    def __str__(self):
        return f"Waitlist for {self.user.username} ({self.email})"