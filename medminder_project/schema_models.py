# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountsReceiveupdates(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=255)
    notifications = models.BooleanField()
    user = models.OneToOneField('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_receiveupdates'


class AccountsTier(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField()
    priority = models.IntegerField()
    is_default = models.BooleanField()
    max_reminders = models.IntegerField(blank=True, null=True)
    max_viewers = models.IntegerField(blank=True, null=True)
    can_use_sms_reminders = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts_tier'


class AccountsUsersettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    receive_email_reminders = models.BooleanField()
    subscription_status = models.CharField(max_length=50)
    payment_customer_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    payment_subscription_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    subscription_end_date = models.DateField(blank=True, null=True)
    account_tier = models.ForeignKey(AccountsTier, models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField('AuthUser', models.DO_NOTHING)
    receive_sms_reminders = models.BooleanField()
    avatar_bg_color = models.CharField(max_length=50)
    avatar_text_color = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'accounts_usersettings'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocumentationDocscategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'documentation_docscategory'


class DocumentationDocstopic(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=50)
    content = models.TextField()
    order_in_category = models.IntegerField()
    category = models.ForeignKey(DocumentationDocscategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'documentation_docstopic'


class RemindersDailyreminderlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    due_date = models.DateField()
    due_time = models.TimeField()
    status = models.CharField(max_length=15)
    reminder = models.ForeignKey('RemindersReminder', models.DO_NOTHING)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    is_notified = models.BooleanField()
    action_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reminders_dailyreminderlog'
        unique_together = (('reminder', 'due_date'),)


class RemindersDosage(models.Model):
    id = models.BigAutoField(primary_key=True)
    dosage = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'reminders_dosage'


class RemindersMedication(models.Model):
    id = models.BigAutoField(primary_key=True)
    medication_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'reminders_medication'


class RemindersReminder(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    dosage = models.ForeignKey(RemindersDosage, models.DO_NOTHING)
    medication = models.ForeignKey(RemindersMedication, models.DO_NOTHING)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    schedule = models.ForeignKey('RemindersSchedule', models.DO_NOTHING)
    is_active = models.BooleanField()
    grace_period = models.DurationField()

    class Meta:
        managed = False
        db_table = 'reminders_reminder'


class RemindersReminderstats(models.Model):
    reminder_stat_id = models.AutoField(primary_key=True)
    date = models.DateField()
    completed = models.BooleanField()
    skipped = models.BooleanField()
    completion_time = models.TimeField(blank=True, null=True)
    reminder = models.ForeignKey(RemindersReminder, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'reminders_reminderstats'


class RemindersSchedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    end_date = models.DateField(blank=True, null=True)
    monthly_dates = models.CharField(max_length=100, blank=True, null=True)
    repeat_type = models.CharField(max_length=10)
    start_date = models.DateField()
    time_of_day = models.TimeField()
    weekly_days = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reminders_schedule'


class RemindersUserstats(models.Model):
    stat_id = models.AutoField(primary_key=True)
    date = models.DateField()
    reminders_completed = models.IntegerField()
    reminders_skipped = models.IntegerField()
    average_compliance = models.FloatField()
    other_stats = models.JSONField(blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    achievement_points = models.IntegerField()
    last_lost_streak_notification_date = models.DateField(blank=True, null=True)
    last_streak_notification_date = models.DateField(blank=True, null=True)
    previous_streak = models.IntegerField()
    last_inactivity_notification_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reminders_userstats'


class RemindersViewer(models.Model):
    viewer_id = models.AutoField(primary_key=True)
    access_granted_at = models.DateTimeField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    viewer_user = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='remindersviewer_viewer_user_set')

    class Meta:
        managed = False
        db_table = 'reminders_viewer'
