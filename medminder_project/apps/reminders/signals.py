from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.timezone import now

from django.contrib.auth import get_user_model
from .models import UserStats

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_stats(sender, instance, created, **kwargs):
    if created:
        UserStats.objects.create(
            user=instance,
            date=now().date(),
        )
