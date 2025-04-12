from django.urls import path, include
from . import views
from .views import ReminderWizard

app_name = 'medminder'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('new-plan/', views.new_plan, name='new_plan'),
    path('add/', ReminderWizard.as_view(views.FORMS, template_name='reminders/forms/wizard_form.html'), name='add_reminder'),
    path('success/', views.reminder_success, name='reminder_success'),
    # path('profile/', views.profile, name='profile'),
    # path('invite-viewer/', views.invite_viewer, name='invite_viewer'),
]