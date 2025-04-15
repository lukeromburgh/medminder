from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
import pdb
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Medication, Dosage, Schedule, Reminder
from .forms import MedicationNameForm, DosageForm, ScheduleForm, ConfirmationForm

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

def new_plan(request):
    """
    Render the new plan page.
    """
    # This is a placeholder for the new plan page view
    # You can add your logic here
    return render(request, 'reminders/reminder_transition.html')


def dashboard (request):
    """
    Render the dashboard page.
    """
    # This is a placeholder for the core page view
    # You can add your logic here
    return render(request, 'reminders/dashboard.html')

# def create_reminder(request):
#     if request.method == 'POST':
#         medication_form = MedicationNameForm(request.POST)
#         dosage_form = DosageForm(request.POST)
#         schedule_form = ScheduleForm(request.POST)

#         if medication_form.is_valid() and dosage_form.is_valid() and schedule_form.is_valid():
#             # 1. Extract cleaned data from the forms
#             medication_name = medication_form.cleaned_data['medication_name']
#             dosage_value = dosage_form.cleaned_data['dosage']
#             repeat_value = schedule_form.cleaned_data['repeat']
#             at_time_value = schedule_form.cleaned_data['at_time']
#             until_date_value = schedule_form.cleaned_data['until_date']

#             # 2. Create model instances
#             medication = Medication.objects.create(medication_name=medication_name)
#             dosage = Dosage.objects.create(dosage=dosage_value)
#             schedule = Schedule.objects.create(
#                 repeat=repeat_value,
#                 at_time=at_time_value,
#                 until_date=until_date_value,
#             )

#             # 3. Create the final Reminder instance
#             reminder = reminder.objects.create(
#                 medication=medication,
#                 dosage=dosage,
#                 schedule=schedule,
#             )

#             return redirect('reminder_created_successfully')  # Redirect to a success page

#     else:
#         medication_form = MedicationNameForm()
#         dosage_form = DosageForm()
#         schedule_form = ScheduleForm()

#     return render(request, 'create_reminder.html', {
#         'medication_form': medication_form,
#         'dosage_form': dosage_form,
#         'schedule_form': schedule_form,
#     })