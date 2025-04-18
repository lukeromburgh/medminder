from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from formtools.wizard.views import SessionWizardView
import pdb
from datetime import timedelta
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Medication, Dosage, Schedule, Reminder, DailyReminderLog, ReminderStats, UserStats
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
                repeat_type=all_data['repeat'],
                weekly_days=all_data.get('weekly_days'), # Use .get for optional fields
                monthly_dates=all_data.get('monthly_dates'),
                time_of_day=all_data['at_time'],
                start_date=all_data['start_date'], # Assuming you added this field
                end_date=all_data.get('until_date'),
                
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
    today = timezone.localdate() # Use timezone.localdate() for the user's local date
    now = timezone.localtime(timezone.now()).time() # Use timezone.localtime() for the user's local time
    user = request.user

    # Total Medications
    # Count active Reminder plans for the user
    # If you want distinct *medications* across plans, your original query is fine:
    # total_medications = Medication.objects.filter(reminder__user=user).distinct().count()
    # If you want total *active reminder plans*, use:
    total_medications = Reminder.objects.filter(user=user, is_active=True).count()


    # --- Fetch Today's Reminders from DailyReminderLog ---
    # Query DailyReminderLog for entries for the current user and today's date
    # Use select_related for efficiency to get related Reminder, Medication, Dosage, Schedule
    todays_reminders = DailyReminderLog.objects.filter(
        user=user,
        due_date=today,
    ).select_related('reminder__medication', 'reminder__dosage', 'reminder__schedule').order_by('due_time')


    # --- Fetch Next Reminder from DailyReminderLog ---
    # Find the next upcoming reminder log entry for the user
    # This requires looking at today's pending reminders *after* the current time,
    # and then potentially looking at future dates if no pending reminders are left today.

    # First, check for pending/upcoming reminders *today* (at or after the current time)
    next_reminder_today = DailyReminderLog.objects.filter(
        user=user,
        due_date=today,
        due_time__gte=now, # Reminders due at or after the current time
        status='pending' # Only consider pending reminders
    ).select_related('reminder__medication', 'reminder__dosage', 'reminder__schedule').order_by('due_time').first()

    next_reminder = None # Initialize next_reminder

    if next_reminder_today:
        next_reminder = next_reminder_today
    else:
        # If no pending reminders left today, find the earliest pending reminder log on a future date
        next_reminder_future = DailyReminderLog.objects.filter(
            user=user,
            due_date__gt=today, # Reminders on dates after today
            status='pending' # Only consider pending reminders
        ).select_related('reminder__medication', 'reminder__dosage', 'reminder__schedule').order_by('due_date', 'due_time').first()
        next_reminder = next_reminder_future


    # --- Weekly Adherence (Last 7 days) from DailyReminderLog ---
    # This calculation needs to use DailyReminderLog entries for the last 7 days
    seven_days_ago = today - timedelta(days=7)

    # Count total logs due in the last 7 days (including today)
    total_logs_last_7_days = DailyReminderLog.objects.filter(
        user=user,
        due_date__gte=seven_days_ago,
        due_date__lte=today # Include today
    ).count()

    # Count completed logs in the last 7 days
    completed_logs_last_7_days = DailyReminderLog.objects.filter(
        user=user,
        due_date__gte=seven_days_ago,
        due_date__lte=today,
        status='completed' # Filter by status
    ).count()

    weekly_adherence = 0
    if total_logs_last_7_days > 0:
        weekly_adherence = (completed_logs_last_7_days / total_logs_last_7_days) * 100
        # weekly_adherence = round(weekly_adherence, 2) # Rounding is done in context


    # --- Achievement Points and Tier ---
    # Assuming UserStats is for cumulative points, not daily
    user_stats, created = UserStats.objects.get_or_create(user=user) # Removed date=today filter
    achievement_points = user_stats.achievement_points
    user_tier = get_user_tier(achievement_points)


    context = {
        'total_medications': total_medications,
        'next_reminder': next_reminder, # This is now a DailyReminderLog object
        'weekly_adherence': round(weekly_adherence, 2), # Round here for template
        'achievement_points': achievement_points,
        'user_tier': user_tier,
        'todays_reminders': todays_reminders, # This is now a QuerySet of DailyReminderLog objects
    }
    # Ensure your template path is correct
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
def complete_reminder(request, reminder_id): # reminder_id here is actually the DailyReminderLog ID
    """Marks a reminder log entry as completed and updates UserStats."""

    # Fetch the specific DailyReminderLog entry using the ID from the URL
    log_entry = get_object_or_404(DailyReminderLog, id=reminder_id, user=request.user)

    if request.method == 'POST':
        # Check if it's already completed to prevent double points
        if log_entry.status == 'pending':
            # Mark the DailyReminderLog entry as completed
            log_entry.status = 'completed'
            log_entry.completion_timestamp = timezone.now() # Record completion time
            log_entry.save()

            # --- Update UserStats ---
            # Assuming UserStats is for cumulative points
            user_stats, created = UserStats.objects.get_or_create(user=request.user) # Removed date filter
            points_earned = 75
            user_stats.achievement_points += points_earned
            user_stats.save()

            points_message = f"Reminder Completed! +{points_earned} Points"
            streak_bonus = 0

            # --- Check and Apply Streak Bonus ---
            # This check_streak function needs to look at DailyReminderLog entries,
            # specifically completed ones, for consecutive dates.
            # You'll need to implement check_streak to use DailyReminderLog data.
            # Example call assuming check_streak(user, days) checks last 'days'
            if check_streak(request.user, 7):
                bonus_points = 300
                user_stats.achievement_points += bonus_points
                user_stats.save()
                points_message += f", 7 Day Streak! +{bonus_points} Points"
                streak_bonus = bonus_points
            elif check_streak(request.user, 3):
                 bonus_points = 100
                 user_stats.achievement_points += bonus_points
                 user_stats.save()
                 points_message += f", 3 Day Streak! +{bonus_points} Points"
                 streak_bonus = bonus_points


            # Return a success JSON response
            return JsonResponse({'message': points_message, 'points': points_earned + streak_bonus})

        else:
             # Reminder was already completed or had another status
             return JsonResponse({'message': 'Reminder already completed or cannot be completed.', 'points': 0}, status=400) # Bad Request


    # If it's not a POST request, redirect
    return redirect('medminder:dashboard_today') # Redirect back to the dashboard


def check_streak(user, days):
    """Checks if the user has a consecutive streak of completed reminders."""
    today = timezone.now().date()
    for i in range(days):
        current_date = today - timezone.timedelta(days=i)
        # Corrected filter: reminder__user=user
        if not ReminderStats.objects.filter(reminder__user=user, date=current_date, completed=True).exists():
            return False
    return True

