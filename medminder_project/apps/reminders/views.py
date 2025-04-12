from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
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
    form_list = FORMS
    template_name = 'reminders/forms/wizard_form.html'  # Generic template for all steps

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]
        # Process the form_data to create your Reminder object
        # For example:
        medication_name = form_data[0]['medication_name']
        dosage = form_data[1]['dosage']
        schedule = form_data[2] # This will be a dictionary of schedule data

        # Save to your Reminder model here
        # ...

        return HttpResponseRedirect('/reminders/success/') # Redirect to a success page

def reminder_success(request):
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
    return render(request, 'base_dashboard.html')