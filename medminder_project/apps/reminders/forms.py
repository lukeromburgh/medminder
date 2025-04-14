from django import forms

class MedicationNameForm(forms.Form):
    medication_name = forms.CharField(label='Medication Name',
                                      widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': 'Enter medication name'
        }))

class DosageForm(forms.Form):
    dosage = forms.CharField(label='Dosage', 
                             widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': 'Enter dosage amount'
        }))

class ScheduleForm(forms.Form):
    repeat = forms.ChoiceField(
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        label='Repeat',
        widget=forms.Select(attrs={  # Use forms.Select for ChoiceField
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 pr-4 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
        })
    )
    at_time = forms.TimeField(
        label='At',
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': '14:00'
        })
    )
    until_date = forms.DateField(
        label='Until',
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': 'End date (YYYY-MM-DD)'
        }),
        required=False
    )

class ConfirmationForm(forms.Form):
    # This form might not have any fields, just used for confirmation
    pass