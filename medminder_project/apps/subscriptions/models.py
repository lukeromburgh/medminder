from django.db import models
from django.conf import settings  # Import settings for User model

class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    insights_access = models.BooleanField(default=False)
    viewer_access = models.BooleanField(default=False)
    other_features = models.JSONField(null=True, blank=True)  # Use JSONField for flexibility

    def __str__(self):
        return self.plan_name

class UserSubscription(models.Model):
    subscription_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use settings.AUTH_USER_MODEL
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=50)  # e.g., 'active', 'pending', 'failed'
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.plan_name}"