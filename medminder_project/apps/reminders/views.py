from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from formtools.wizard.views import SessionWizardView
import pdb
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Medication, Dosage, Schedule, Reminder, ReminderStats, UserStats
from .forms import MedicationNameForm, DosageForm, ScheduleForm, ConfirmationForm
from django.contrib.auth.decorators import login_required 

FORMS = [("medication", MedicationNameForm),
         ("dosage", DosageForm),
         ("schedule", ScheduleForm),
         ("confirmation", ConfirmationForm)]

TEMPLATES = {'medication': 'reminders/forms/medication_form.html',
             'dosage': 'reminders/forms/dosage_form.html',
             'schedule': 'reminders/forms/schedule_form.html',
             'confirmation': 'reminders/forms/confirmation_form.html'}

class ReminderWizard(SessionWizardView):
    # template_name = "reminders/forms/wizard_form.html" # This is a fallback, get_template_names is primary

    def get_template_names(self):
        # Ensure this returns the correct template for the current step
        return [TEMPLATES[self.steps.current]]

    # Add this method to provide context specifically for the confirmation step's template
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        # When rendering the 'confirmation' step, add the collected data to the context
        if self.steps.current == 'confirmation':
            context['all_data'] = self.get_all_cleaned_data()
            # You can add debugging here to check context['all_data']
            print("Context for confirmation step:", context['all_data'])
        return context

    def done(self, form_list, **kwargs):
        print("Done method called")  # Debug
        # This method runs *after* the confirmation step is submitted.
        # It should process the data and redirect.
        all_data = self.get_all_cleaned_data()
        print(f"All data: {all_data}")  # Debug

        # Optional: Add validation/error handling if all_data is unexpectedly empty
        if not all_data:
             print("Error in done method: Cleaned data is empty. Check session storage and form validation.")
             # Redirect to the start or an error page might be appropriate
             print("Redirecting to add_reminder due to empty data.")
             return redirect('medminder:add_reminder') # Redirecting to the start

        # Create model instances using the collected data
        try:
            medication = Medication.objects.create(
                medication_name=all_data['medication_name'] # Access directly if confident keys exist
            )
            dosage = Dosage.objects.create(
                dosage=all_data['dosage']
            )
            schedule = Schedule.objects.create(
                repeat=all_data['repeat'],
                at_time=all_data['at_time'],
                until_date=all_data.get('until_date') # Use .get() for optional fields
            )
            # Assuming Reminder model doesn't need user, otherwise add it
            reminder = Reminder.objects.create(
                medication=medication,
                dosage=dosage,
                schedule=schedule,
                user=self.request.user # If reminders are user-specific and user is logged in
            )
        except KeyError as e:
            print(f"Error in done method: Missing key in all_data - {e}")
            # Handle missing data, perhaps redirect back to the start or an error page
            return redirect('medminder:add_reminder')
        except Exception as e:
            print(f"Error saving reminder: {e}")
            # Handle generic database errors
            # Consider adding a message to the user
            return redirect('medminder:add_reminder') # Or an error page
        self.storage.reset()

        # Redirect to the success page after saving
        print("Redirecting to reminder_success")  # Debug
        return redirect('medminder:reminder_success')


def reminder_success(request):
    """
    Render the reminder success page.
    """
    return render(request, 'reminders/reminder_success.html')

@login_required
def new_plan(request):
    """
    Render the new plan page.
    """
    user = request.user
    context = {
        'user': user,
    }
    # This is a placeholder for the new plan page view
    # You can add your logic here
    return render(request, 'reminders/reminder_transition.html', context)


@login_required
def dashboard_today(request):
    """Displays the user's dashboard with today's reminders and stats."""
    today = timezone.now().date()
    now = timezone.now().time()
    user = request.user

    # Total Medications
    total_medications = Medication.objects.filter(reminder__user=user).distinct().count()

    # Next Reminder (Get the next incomplete reminder)
    next_reminder = Reminder.objects.filter(user=user, due_date__gte=today, completed=False).order_by('due_date', 'due_time').first()

    # Weekly Adherence (Last 7 days)
    last_7_days = [today - timezone.timedelta(days=i) for i in range(7)]
    completed_count = ReminderStats.objects.filter(reminder__user=user, date__in=last_7_days, completed=True).count()
    total_count = ReminderStats.objects.filter(reminder__user=user, date__in=last_7_days).count()
    weekly_adherence = (completed_count / total_count * 100) if total_count > 0 else 0

    # Achievement Points and Tier
    user_stats, created = UserStats.objects.get_or_create(user=user, date=today)
    achievement_points = user_stats.achievement_points
    user_tier = get_user_tier(achievement_points)

    # Fetch reminders for the current user for today.
    todays_reminders = Reminder.objects.filter(
        user=user,
        due_date=today,
    ).order_by('due_time')

    context = {
        'total_medications': total_medications,
        'next_reminder': next_reminder,
        'weekly_adherence': round(weekly_adherence, 2),
        'achievement_points': achievement_points,
        'user_tier': user_tier,
        'todays_reminders': todays_reminders,
    }
    return render(request, 'reminders/dashboard_today.html', context)

def get_user_tier(points):
    """Determines the user's tier based on achievement points."""
    if points >= 10000:
        return "Diamond Legend"
    elif points >= 7500:
        return "Emerald Elite"
    elif points >= 5000:
        return "Ruby Master"
    elif points >= 3000:
        return "Sapphire Champion"
    elif points >= 1500:
        return "Gold Guardian"
    elif points >= 750:
        return "Silver Sentinel"
    elif points >= 300:
        return "Bronze Beginner"
    else:
        return "Iron Initiate"

@login_required
def complete_reminder(request, reminder_id):
    """Marks a reminder as completed and updates UserStats."""
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        reminder.completed = True
        reminder.save()

        ReminderStats.objects.create(
            reminder=reminder,
            date=timezone.now().date(),
            completed=True,
        )

        user_stats, created = UserStats.objects.get_or_create(user=request.user, date=timezone.now().date())
        user_stats.achievement_points += 75
        user_stats.save()

        points_message = "Reminder Completed! +75 Points"
        streak_bonus = 0

        if check_streak(request.user, 7):
            user_stats.achievement_points += 300
            user_stats.save()
            points_message += ", 7 Day Streak! +300 Points"
            streak_bonus = 300
        elif check_streak(request.user, 3):
            user_stats.achievement_points += 100
            user_stats.save()
            points_message += ", 3 Day Streak! +100 Points"
            streak_bonus = 100

        return JsonResponse({'message': points_message, 'points': 75 + streak_bonus})
    return redirect('medminder:dashboard')

def check_streak(user, days):
    """Checks if the user has a consecutive streak of completed reminders."""
    today = timezone.now().date()
    for i in range(days):
        current_date = today - timezone.timedelta(days=i)
        # Corrected filter: reminder__user=user
        if not ReminderStats.objects.filter(reminder__user=user, date=current_date, completed=True).exists():
            return False
    return True

