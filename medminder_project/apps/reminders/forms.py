from django import forms

class MedicationNameForm(forms.Form):
    medication_name = forms.CharField(label='Medication Name')

class DosageForm(forms.Form):
    dosage = forms.CharField(label='Dosage')

class ScheduleForm(forms.Form):
    repeat = forms.ChoiceField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], label='Repeat')
    at_time = forms.TimeField(label='At')
    until_date = forms.DateField(label='Until', required=False)

class ConfirmationForm(forms.Form):
    # This form might not have any fields, just used for confirmation
    pass