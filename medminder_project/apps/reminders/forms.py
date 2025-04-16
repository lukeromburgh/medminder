# forms.py
from django import forms
import datetime

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
    REPEAT_CHOICES = [
        ('', 'Never'), # Add a default empty choice
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    # Keep track of days using integers (0=Mon, 1=Tue, ..., 6=Sun) - consistent with Python's weekday()
    DAYS_OF_WEEK = [
        ('0', 'M'), ('1', 'T'), ('2', 'W'), ('3', 'T'), ('4', 'F'), ('5', 'S'), ('6', 'S')
    ]

    repeat = forms.ChoiceField(
        choices=REPEAT_CHOICES,
        label='Repeat',
        required=True, # Make sure a choice is selected
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 pr-4 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'id': 'id_repeat_select', # Add ID for JS targeting
        })
    )
    at_time = forms.TimeField(
        label='At',
        widget=forms.TimeInput(format='%H:%M', attrs={ # Use TimeInput for better browser support
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': 'HH:MM (e.g., 14:00)',
            'type': 'time', # Use HTML5 time input where possible
        })
    )
    until_date = forms.DateField(
        label='Until',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={ # Use DateInput
            'class': 'mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm',
            'placeholder': 'End date (DD--MM-YY)',
            'type': 'date', # Use HTML5 date input where possible
        }),
        required=False
    )

    # Hidden fields to store selections from JS widgets
    # Store weekly days as comma-separated integers (0-6)
    weekly_days = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'id_weekly_days_hidden'}), required=False)
    # Store monthly dates as comma-separated YYYY-MM-DD strings
    monthly_dates = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'id_monthly_dates_hidden'}), required=False)

    # --- Validation ---
    def clean_weekly_days(self):
        """Validate weekly_days only if repeat is 'weekly'."""
        repeat = self.cleaned_data.get('repeat')
        weekly_days_str = self.cleaned_data.get('weekly_days')

        if repeat == 'weekly':
            if not weekly_days_str:
                raise forms.ValidationError("Please select at least one day for weekly repetition.")
            # Further validate if needed (e.g., check if values are 0-6)
            try:
                days = [int(d) for d in weekly_days_str.split(',') if d]
                if not all(0 <= day <= 6 for day in days):
                     raise ValueError("Invalid day number.")
                return weekly_days_str # Return the original string for now, process in clean()
            except (ValueError, TypeError):
                 raise forms.ValidationError("Invalid day format selected.")
        return weekly_days_str # Return None or the string if not weekly

    def clean_monthly_dates(self):
        """Validate monthly_dates only if repeat is 'monthly'."""
        repeat = self.cleaned_data.get('repeat')
        monthly_dates_str = self.cleaned_data.get('monthly_dates')

        if repeat == 'monthly':
            if not monthly_dates_str:
                raise forms.ValidationError("Please select at least one date for monthly repetition.")
            # Further validate if needed (e.g., check if values are valid dates)
            try:
                dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in monthly_dates_str.split(',') if date]
                if not dates: # Handle case where split resulted in empty list
                    raise forms.ValidationError("Please select at least one date for monthly repetition.")
                return monthly_dates_str # Return the original string for now, process in clean()
            except (ValueError, TypeError):
                 raise forms.ValidationError("Invalid date format selected.")
        return monthly_dates_str # Return None or the string if not monthly

    def clean(self):
        """
        Process the hidden field data into more usable formats (list of ints/dates)
        after individual field validation.
        """
        cleaned_data = super().clean()
        repeat = cleaned_data.get('repeat')
        weekly_days_str = cleaned_data.get('weekly_days')
        monthly_dates_str = cleaned_data.get('monthly_dates')

        # Clear the data for the non-selected repeat type
        if repeat == 'weekly':
            cleaned_data['monthly_dates'] = None # Clear monthly dates if weekly is chosen
            if weekly_days_str:
                 try:
                     # Convert comma-separated string '0,2,4' to list of integers [0, 2, 4]
                     cleaned_data['selected_week_days'] = sorted([int(d) for d in weekly_days_str.split(',') if d])
                 except (ValueError, TypeError):
                     # This should ideally be caught in clean_weekly_days, but handle defensively
                     self.add_error('weekly_days', "Invalid day format processing.")
            else:
                 # This case is handled by clean_weekly_days raising an error if required
                 pass

        elif repeat == 'monthly':
            cleaned_data['weekly_days'] = None # Clear weekly days if monthly is chosen
            if monthly_dates_str:
                try:
                    # Convert comma-separated string '2024-05-10,2024-05-25' to list of date objects
                    cleaned_data['selected_month_dates'] = sorted([
                        datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        for date_str in monthly_dates_str.split(',') if date_str
                    ])
                except (ValueError, TypeError):
                    # This should ideally be caught in clean_monthly_dates, but handle defensively
                    self.add_error('monthly_dates', "Invalid date format processing.")
            else:
                # This case is handled by clean_monthly_dates raising an error if required
                pass
        else: # daily or other types
            cleaned_data['weekly_days'] = None
            cleaned_data['monthly_dates'] = None
            cleaned_data['selected_week_days'] = None
            cleaned_data['selected_month_dates'] = None

        return cleaned_data


class ConfirmationForm(forms.Form):
    # This form might not have any fields, just used for confirmation
    pass