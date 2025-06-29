from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reminders"

    def ready(self):
        # Local import to avoid premature model access
        import apps.reminders.signals
