from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView


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
    template_name = "reminders/forms/wizard_form.html"

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        all_data = {}
        for form in form_list:
            all_data.update(form.cleaned_data)

        # Create model instances (as you were doing before, or modify as needed)
        medication = Medication.objects.create(medication_name=all_data['medication_name'])
        dosage = Dosage.objects.create(dosage=all_data['dosage'])
        schedule = Schedule.objects.create(
            repeat=all_data['repeat'],
            at_time=all_data['at_time'],
            until_date=all_data.get('until_date')  # Use .get() in case it's not always provided
        )

        reminder = Reminder.objects.create(
            medication=medication,
            dosage=dosage,
            schedule=schedule,
        )

        return render(self.request, 'reminders/forms/confirmation_form.html', {'all_data': all_data, 'reminder': reminder})

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

def create_reminder(request):
    if request.method == 'POST':
        medication_form = MedicationNameForm(request.POST)
        dosage_form = DosageForm(request.POST)
        schedule_form = ScheduleForm(request.POST)

        if medication_form.is_valid() and dosage_form.is_valid() and schedule_form.is_valid():
            # 1. Extract cleaned data from the forms
            medication_name = medication_form.cleaned_data['medication_name']
            dosage_value = dosage_form.cleaned_data['dosage']
            repeat_value = schedule_form.cleaned_data['repeat']
            at_time_value = schedule_form.cleaned_data['at_time']
            until_date_value = schedule_form.cleaned_data['until_date']

            # 2. Create model instances
            medication = Medication.objects.create(medication_name=medication_name)
            dosage = Dosage.objects.create(dosage=dosage_value)
            schedule = Schedule.objects.create(
                repeat=repeat_value,
                at_time=at_time_value,
                until_date=until_date_value,
            )

            # 3. Create the final Reminder instance
            reminder = reminder.objects.create(
                medication=medication,
                dosage=dosage,
                schedule=schedule,
            )

            return redirect('reminder_created_successfully')  # Redirect to a success page

    else:
        medication_form = MedicationNameForm()
        dosage_form = DosageForm()
        schedule_form = ScheduleForm()

    return render(request, 'create_reminder.html', {
        'medication_form': medication_form,
        'dosage_form': dosage_form,
        'schedule_form': schedule_form,
    })