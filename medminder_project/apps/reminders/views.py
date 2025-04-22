from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from formtools.wizard.views import SessionWizardView
# import pdb # Keep or remove based on your debugging needs
from datetime import timedelta, date # Import date
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
# Import necessary models
# Note: ReminderStats model definition is assumed for check_streak
from .models import Medication, Dosage, Schedule, Reminder, DailyReminderLog, ReminderStats, UserStats
# Import necessary forms
from .forms import MedicationNameForm, DosageForm, ScheduleForm, ConfirmationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q # Import Q for complex queries
import json # Import json for potentially parsing schedule data


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
            # print("Context for confirmation step:", context['all_data']) # Uncomment for debugging
        return context

    def done(self, form_list, **kwargs):
        # --- Add these print statements ---
        print("--- ReminderWizard done() method called ---")
        all_data = self.get_all_cleaned_data()
        print(f"--- all_data: {all_data} ---")

        # Optional: Add validation/error handling if all_data is unexpectedly empty
        if not all_data:
             print("--- Error in done method: Cleaned data is empty. Redirecting to add_reminder. ---")
             return redirect('medminder:add_reminder') # Redirecting to the start

        # Create model instances using the collected data
        try:
            print("--- Attempting to create model instances ---")

            print("--- Getting/Creating Medication ---")
            medication, created_med = Medication.objects.get_or_create(
                medication_name=all_data['medication_name']
            )
            print(f"--- Medication: {medication}, Created: {created_med} ---")

            print("--- Getting/Creating Dosage ---")
            dosage, created_dos = Dosage.objects.get_or_create(
                dosage=all_data['dosage']
            )
            print(f"--- Dosage: {dosage}, Created: {created_dos} ---")

            # Handle weekly_days and monthly_dates storage...
            weekly_days_data = all_data.get('weekly_days')
            monthly_dates_data = all_data.get('monthly_dates')

            if isinstance(weekly_days_data, list):
                 weekly_days_data = ','.join(map(str, weekly_days_data))
            weekly_days_data = weekly_days_data if weekly_days_data else ''

            if isinstance(monthly_dates_data, list):
                 monthly_dates_data = ','.join(map(str, monthly_dates_data))
            monthly_dates_data = monthly_dates_data if monthly_dates_data else ''

            print("--- Creating Schedule ---")
            schedule = Schedule.objects.create(
                repeat_type=all_data['repeat'],
                weekly_days=weekly_days_data,
                monthly_dates=monthly_dates_data,
                time_of_day=all_data['at_time'],
                start_date=all_data['start_date'],
                end_date=all_data.get('until_date'),
            )
            print(f"--- Schedule created: {schedule} ---")

            print("--- Creating Reminder ---")
            # Ensure the user is associated with the reminder.
            # Assuming request.user is available and the user is logged in due to @login_required
            reminder = Reminder.objects.create(
                medication=medication,
                dosage=dosage,
                schedule=schedule,
                user=self.request.user # Make sure the user is being correctly assigned
            )
            print(f"--- Reminder created: {reminder} ---")


            # Optional: Immediately generate today's DailyReminderLog...
            today = timezone.localdate()
            # Check if reminder is active *and* starts today or earlier
            if reminder.is_active and reminder.schedule.start_date <= today and (reminder.schedule.end_date is None or today <= reminder.schedule.end_date):
                 today_weekday = today.weekday()
                 today_day_of_month = today.day
                 is_due_today = False
                 # ... (repeat type checks for is_due_today) ... # Keep your existing logic here

                 if schedule.repeat_type == 'daily':
                      is_due_today = True
                 elif schedule.repeat_type == 'weekly' and schedule.weekly_days:
                      try:
                           weekly_days_list = [int(day.strip()) for day in schedule.weekly_days.split(',') if day.strip()]
                           if today_weekday in weekly_days_list:
                                is_due_today = True
                      except ValueError:
                           pass
                 elif schedule.repeat_type == 'monthly' and schedule.monthly_dates:
                      try:
                           monthly_dates_list = [int(day.strip()) for day in schedule.monthly_dates.split(',') if day.strip()]
                           if 1 <= today_day_of_month <= 31 and today_day_of_month in monthly_dates_list:
                                is_due_today = True
                      except ValueError:
                           pass
                 elif schedule.repeat_type == 'once' and schedule.start_date == today:
                     is_due_today = True


                 if is_due_today:
                      print("--- Generating today's DailyReminderLog entry ---")
                      DailyReminderLog.objects.get_or_create(
                           user=self.request.user,
                           reminder=reminder,
                           due_date=today,
                           due_time=schedule.time_of_day,
                           defaults={'status': 'pending'}
                      )
                      print("--- DailyReminderLog entry generated ---")


        except KeyError as e:
            print(f"--- KeyError in done method: Missing key - {e} ---")
            # This means a form field name expected in all_data was not present.
            print("--- Redirecting to add_reminder due to KeyError ---")
            # Consider adding a message to the user indicating which field was missing.
            return redirect('medminder:add_reminder')
        except Exception as e:
            print(f"--- General Exception in done method: {e} ---")
            # Print the full traceback for debugging to see the exact error and line number
            import traceback
            traceback.print_exc()
            print("--- Redirecting to add_reminder due to Exception ---")
            # Consider adding a user-friendly error message using Django messages.
            return redirect('medminder:add_reminder')


        self.storage.reset() # Clear wizard data
        print("--- Wizard storage reset ---")

        # Redirect to the success page after saving
        print("--- Redirecting to reminder_success ---")
        return redirect('medminder:reminder_success')


def reminder_success(request):
    """
    Render the reminder success page.
    """
    return render(request, 'reminders/reminder_success.html')

@login_required
def new_plan(request):
    """
    Render the new plan page (likely just a transition page before the wizard).
    Or, this view could simply redirect to the first step of the wizard.
    """
    user = request.user
    context = {
        'user': user,
    }
    # This is a placeholder. You might just redirect to the wizard entry point here.
    return render(request, 'reminders/reminder_transition.html', context)


@login_required # Ensure the user is logged in
def all_medications(request):
    """Displays a list of all active medication plans for the user."""
    user = request.user

    # Fetch all active Reminder objects for the user
    # Use select_related for efficiency to get related Medication, Dosage, Schedule
    # Order by medication name and then time for better organization
    all_reminders = Reminder.objects.filter(
        user=user,
        is_active=True # Assuming you have an is_active field on Reminder model
    ).select_related('medication', 'dosage', 'schedule').order_by('medication__medication_name', 'schedule__time_of_day')

    context = {
        'all_reminders': all_reminders, # Pass the list of all active reminders
    }

    # Render the new template (assuming you named it medications_list.html or similar)
    return render(request, 'reminders/medications.html', context) # Changed template name to match our previous step


@login_required
def dashboard_today(request):
    """
    Displays the user's dashboard with today's reminders and stats.
    Generates DailyReminderLog entries for today if they don't exist
    based on the user's active Reminder schedules.
    """
    today = timezone.localdate() # Use timezone.localdate() for the user's local date
    now = timezone.localtime(timezone.now()).time() # Use timezone.localtime() for the user's local time
    user = request.user

    # --- STEP 1: GENERATE TODAY'S DAILY REMINDER LOGS ---
    # This logic runs every time the dashboard is loaded to ensure logs are present.
    # For larger applications, consider moving this to a daily background task (cron job/Celery).
    # However, placing it here ensures the dashboard is always up-to-date for the user.

    # Find all active reminder plans for the user that started on or before today
    # Use select_related to get schedule info efficiently
    active_reminders_due_today_or_later = Reminder.objects.filter(
        user=user,
        is_active=True, # Filter for active reminders
        schedule__start_date__lte=today # Only consider reminders that have started on or before today
    ).select_related('schedule')


    # Get today's weekday (0=Monday, 6=Sunday) and day of the month
    today_weekday = today.weekday() # Returns integer 0-6
    today_day_of_month = today.day

    for reminder in active_reminders_due_today_or_later:
        schedule = reminder.schedule

        # Check if today is within the reminder's end date range (already started filter is above)
        is_within_end_date_range = (schedule.end_date is None or today <= schedule.end_date)

        if not is_within_end_date_range:
            continue # Skip this reminder if it ended before today

        # Determine if the reminder is scheduled for today based on its repeat type
        is_due_today = False

        if schedule.repeat_type == 'daily':
            is_due_today = True
        elif schedule.repeat_type == 'weekly':
            # Check if today's weekday is in the weekly_days field
            # --- ASSUMPTION: weekly_days is stored as a comma-separated string of weekday integers (0-6) ---
            # Added strip() and error handling for robustness
            if schedule.weekly_days: # Ensure the field is not empty or None
                 try:
                     # Attempt to parse weekly_days as a comma-separated string of integers
                     weekly_days_list = [int(day.strip()) for day in schedule.weekly_days.split(',') if day.strip()]
                     if today_weekday in weekly_days_list:
                         is_due_today = True
                 except ValueError:
                      # Handle potential errors in stored data format - Treat as not due today
                      # print(f"Warning: Invalid data in weekly_days for Reminder ID {reminder.id}: {schedule.weekly_days}") # Debug
                      pass # Assume not due today if data is malformed

        elif schedule.repeat_type == 'monthly':
             # Check if today's day of the month is in the monthly_dates field
             # --- ASSUMPTION: monthly_dates is stored as a comma-separated string of day integers (1-31) ---
             # Added strip() and error handling for robustness
             if schedule.monthly_dates: # Ensure the field is not empty or None
                  try:
                       # Attempt to parse monthly_dates as a comma-separated string of integers
                       monthly_dates_list = [int(day.strip()) for day in schedule.monthly_dates.split(',') if day.strip()]
                       # Ensure the day of the month is valid (e.g., prevent checking for day 31 in February)
                       if 1 <= today_day_of_month <= 31 and today_day_of_month in monthly_dates_list:
                           is_due_today = True
                  except ValueError:
                       # Handle potential errors in stored data format - Treat as not due today
                       # print(f"Warning: Invalid data in monthly_dates for Reminder ID {reminder.id}: {schedule.monthly_dates}") # Debug
                       pass # Assume not due today if data is malformed

        # Add other repeat types here if necessary (e.g., 'once', 'yearly')
        # For 'once', check if today is the start date
        elif schedule.repeat_type == 'once' and schedule.start_date == today:
            is_due_today = True


        if is_due_today:
            # Check if a DailyReminderLog entry already exists for this specific reminder, user, date, and time
            # Use get_or_create for atomicity and to prevent duplicates if run concurrently
            log_entry, created = DailyReminderLog.objects.get_or_create(
                user=user, # Keyword argument
                reminder=reminder, # Keyword argument
                due_date=today, # Keyword argument
                due_time=schedule.time_of_day, # Keyword argument
                defaults={'status': 'pending'} # Keyword argument 'defaults'
            )
            # If 'created' is False, the entry already existed

    # --- STEP 2: FETCH TODAY'S DAILY REMINDER LOGS (NOW GUARANTEED TO BE GENERATED IF DUE) ---
    # Query DailyReminderLog for entries for the current user and today's date
    # Use select_related for efficiency
    # Order by due_time to display them chronologically on the dashboard
    todays_reminders = DailyReminderLog.objects.filter(
        user=user,
        due_date=today,
    ).select_related('reminder__medication', 'reminder__dosage', 'reminder__schedule').order_by('due_time')


    # --- STEP 3: FETCH NEXT REMINDER from DailyReminderLog ---
    # Find the next upcoming reminder log entry for the user
    # This requires looking at today's pending reminders *after* the current time,
    # and then potentially looking at future dates if no pending reminders are left today.

    # Corrected the filter order: Q objects must come before keyword arguments
    upcoming_logs_query = DailyReminderLog.objects.filter(
        # Place Q objects first
        Q(due_date=today, due_time__gte=now) | Q(due_date__gt=today),
        # Then place keyword arguments
        user=user,
        status='pending' # Only consider pending reminders
    )

    # Order first by date, then by time, and get the first one
    next_reminder = upcoming_logs_query.select_related(
        'reminder__medication', 'reminder__dosage', 'reminder__schedule'
    ).order_by('due_date', 'due_time').first()


    # Weekly Adherence Calculation (Example - adjust as needed)
    one_week_ago = today - timedelta(days=7)
    logs_last_week = DailyReminderLog.objects.filter(
        user=user,
        due_date__gte=one_week_ago,
        due_date__lte=today # Include today
    )
    completed_last_week = logs_last_week.filter(status='completed').count()
    total_due_last_week = logs_last_week.count() # Or count distinct days if needed
    weekly_adherence = int((completed_last_week / total_due_last_week * 100)) if total_due_last_week > 0 else 100

    # Achievement Points / Tier (Example - fetch from UserStats or calculate)
    user_stats, _ = UserStats.objects.get_or_create(user=user)
    achievement_points = user_stats.achievement_points
    user_tier = get_user_tier(achievement_points) # Assuming you have a get_tier_display method or similar


    # --- STEP 5: CALCULATE ADHERENCE DATA FOR TRACKER WIDGET ---
    adherence_data = {}
    current_streak_count = calculate_current_adherence_streak(user)
    # Calculate for the last year (adjust range if needed)
    start_date_year = today - timedelta(days=365)
    # Or align to the start of the week/month if preferred for display

    # Get all relevant logs in the period
    logs_for_tracker = DailyReminderLog.objects.filter(
        user=user,
        due_date__gte=start_date_year,
        due_date__lte=today
    ).values('due_date', 'status') # Get only necessary fields

    # Group logs by date
    logs_by_date = {}
    for log in logs_for_tracker:
        log_date = log['due_date']
        if log_date not in logs_by_date:
            logs_by_date[log_date] = {'completed': 0, 'pending': 0, 'total': 0}
        logs_by_date[log_date]['total'] += 1
        if log['status'] == 'completed':
            logs_by_date[log_date]['completed'] += 1
        elif log['status'] == 'pending': # Treat past pending as missed for visualization
             logs_by_date[log_date]['pending'] += 1
        # Add other statuses ('skipped', 'missed' if you implement them)

    # Determine adherence level for each day in the past year
    current_date = start_date_year
    while current_date <= today:
        date_str = current_date.isoformat() # YYYY-MM-DD format
        if current_date in logs_by_date:
            day_data = logs_by_date[current_date]
            # Define adherence levels (customize as needed)
            if day_data['pending'] > 0 and current_date < today: # Past day with pending logs = missed
                adherence_data[date_str] = 1 # Level 1: Missed/Partial
            elif day_data['completed'] == day_data['total']:
                adherence_data[date_str] = 3 # Level 3: Fully Completed
            elif day_data['completed'] > 0:
                adherence_data[date_str] = 2 # Level 2: Partially Completed
            else: # All pending for today (or only future logs scheduled)
                adherence_data[date_str] = 0 # Level 0: Nothing Completed/Pending Today
        else:
            # Check if any reminders *should* have been scheduled for this day (more complex)
            # For simplicity now, assume no logs means nothing was due or logged
            adherence_data[date_str] = 0 # Level 0: No activity / Nothing due

        current_date += timedelta(days=1)

    # Convert adherence data to JSON for the template
    adherence_data_json = json.dumps(adherence_data)


    # --- Total Medications ---
    # This remains the count of active Reminder plans
    total_medications = Reminder.objects.filter(user=user, is_active=True).count()


    context = {
        'total_medications': total_medications,
        'next_reminder': next_reminder, # This is the DailyReminderLog object for the next reminder
        'weekly_adherence': round(weekly_adherence, 2), # Round here for template
        'achievement_points': achievement_points,
        'user_tier': user_tier,
        'todays_reminders': todays_reminders, # This is now the correctly generated list of today's DailyReminderLog entries
        'adherence_data_json': adherence_data_json, # Add adherence data
        'current_streak_count': current_streak_count,
    }

    # Ensure your template path is correct
    return render(request, 'reminders/dashboard_today.html', context)


# Assuming get_user_tier is defined elsewhere, e.g.:
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
    # Ensure it belongs to the current user
    log_entry = get_object_or_404(DailyReminderLog, id=reminder_id, user=request.user)

    if request.method == 'POST':
        # Check if it's already completed to prevent double points/streak issues
        if log_entry.status == 'pending':
            # Mark the DailyReminderLog entry as completed
            log_entry.status = 'completed'
            log_entry.completion_timestamp = timezone.now() # Record completion time
            log_entry.save()

            # --- Update UserStats ---
            # UserStats is for cumulative points and tier
            user_stats, created = UserStats.objects.get_or_create(user=request.user)
            points_earned = 75 # Base points for completing a reminder
            user_stats.achievement_points += points_earned

            points_message = f"Reminder Completed! +{points_earned} Points"
            streak_bonus = 0

            # --- Check and Apply Streak Bonus based on Daily Completion Summary in ReminderStats ---
            # This logic awards bonus points based on the streak check using ReminderStats.
            # IMPORTANT: For this to work correctly, a separate process MUST
            # update the ReminderStats table daily based on whether the user
            # met the completion criteria for that day (e.g., completed at least one reminder).
            # The check_streak function below queries ReminderStats based on this assumption.
            if check_streak(request.user, 7):
                bonus_points = 300
                user_stats.achievement_points += bonus_points
                points_message += f", 7 Day Streak! +{bonus_points} Bonus!"
                streak_bonus = bonus_points
            elif check_streak(request.user, 3):
                 bonus_points = 100
                 user_stats.achievement_points += bonus_points
                 points_message += f", 3 Day Streak! +{bonus_points} Bonus!"
                 streak_bonus = bonus_points

            user_stats.save() # Save UserStats after adding points/bonus

            # Return a success JSON response
            # Include user's new total points and tier for potential UI updates
            return JsonResponse({
                'message': points_message,
                'points_earned_today': points_earned + streak_bonus, # Points earned from this action
                'total_points': user_stats.achievement_points, # User's new total cumulative points
                'user_tier': get_user_tier(user_stats.achievement_points) # User's new tier
            })

        else:
             # Reminder was already completed or had another status (e.g., skipped)
             # Return a 400 Bad Request or similar, and a message
             return JsonResponse({'message': 'Reminder already completed or cannot be completed.', 'points_earned_today': 0}, status=400)


    # If it's not a POST request, redirect (shouldn't happen from the dashboard UI)
    return redirect('medminder:dashboard_today')


# --- check_streak function operating on ReminderStats as requested ---
# --- check_streak function operating on ReminderStats as requested ---
def check_streak(user, days):
    """
    Checks if the user has a consecutive streak of days where *at least one*
    ReminderStats entry exists for a reminder owned by that user and is marked as 'completed=True'.

    This function assumes ReminderStats has a 'reminder' ForeignKey (linking to a Reminder model),
    a 'date' field (DateField), and a boolean field named 'completed'.

    Overall progression in this context is interpreted as the historical record of
    daily completion summaries stored in the ReminderStats table, where a 'completed' day
    for the user is marked by having at least one relevant ReminderStats entry completed.

    CRITICAL REQUIREMENT: This function ONLY reads the ReminderStats table.
    A separate daily background task is REQUIRED to populate and update the
    ReminderStats table correctly based on the user's performance in
    DailyReminderLog for the previous day. Without this daily update process,
    the streak calculation will not work as intended.
    """
    today = timezone.now().date() # Get today's date in the current timezone

    # Removed the get_or_create for today's stat here, as it's ambiguous
    # if ReminderStats is per-reminder. The daily background task must handle
    # creating/updating the relevant ReminderStats entries.

    for i in range(days):
        current_date = today - timezone.timedelta(days=i)

        # Check if *any* ReminderStats entry exists for *any* reminder owned by this user
        # for the current_date, where that specific entry is marked completed=True.
        # This implements the streak as requiring *at least one* successfully completed
        # ReminderStats entry associated with a user's reminder per day.
        day_has_completed_stat = ReminderStats.objects.filter(
            reminder__user=user, # <--- Ensure this line uses reminder__user=user
            date=current_date,
            completed=True # Assumed boolean field indicating completion for *that specific stat entry's reminder* on that day
        ).exists()

        if not day_has_completed_stat:
             # If no ReminderStats entry exists for this user on this date that is marked completed,
             # the streak is broken for this day.
            return False # Streak is broken

    # If the loop completes, it means at least one completed ReminderStats entry was found
    # for a reminder owned by the user for all 'days' consecutively.
    return True

def calculate_current_adherence_streak(user):
    """
    Calculates the number of consecutive days ending today where the user
    has at least one completed ReminderStats entry.
    """
    today = timezone.now().date()
    streak_count = 0
    current_date = today

    while True:
        # Check if the user has any completed ReminderStats for the current date
        has_adherence = ReminderStats.objects.filter(
            reminder__user=user,  # Assuming Reminder model has a ForeignKey to User
            date=current_date,
            completed=True
        ).exists()

        if has_adherence:
            streak_count += 1
            current_date -= timedelta(days=1)
        else:
            break  # Streak broken

        # Optional: Add a reasonable limit to prevent infinite loops in case of issues
        if streak_count > 365:  # Example limit of one year
            break

    return streak_count