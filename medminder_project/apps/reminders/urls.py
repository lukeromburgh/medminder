from django.urls import path, include
from . import views
from .views import ReminderWizard

app_name = 'medminder'

urlpatterns = [
    path('', views.dashboard_today, name='dashboard'),
    path('dashboard', views.dashboard_today, name='dashboard'),
    path('new-plan/', views.new_plan, name='new_plan'),
    path('add/', ReminderWizard.as_view(views.FORMS, template_name='reminders/forms/wizard_form.html'), name='add_reminder'),
    path('reminder/success/', views.reminder_success, name='reminder_success'),
    path('complete/<int:reminder_id>/', views.complete_reminder, name='complete_reminder'),
    path('medications', views.all_medications, name='medications'),
    path('dashboard/calendar/', views.dashboard_calendar, name='dashboard_calendar'), # New URL for the calendar
    path('account', views.account_page_view, name='account_page'),
    path('delete-reminder/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    # path('profile/', views.profile, name='profile'),
    # path('invite-viewer/', views.invite_viewer, name='invite_viewer'),
]