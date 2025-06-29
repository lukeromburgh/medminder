# forms.py
from django import forms
import datetime


class MedicationNameForm(forms.Form):
    medication_name = forms.CharField(
        label="Medication Name",
        widget=forms.TextInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "placeholder": "Enter medication name",
            }
        ),
    )


class DosageForm(forms.Form):
    dosage = forms.CharField(
        label="Dosage",
        widget=forms.TextInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "placeholder": "Enter dosage amount",
            }
        ),
    )


class ScheduleForm(forms.Form):
    REPEAT_CHOICES = [
        ("", "Never"),  # Add a default empty choice for no repetition
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        # Add yearly if needed
    ]
    # Keep track of days using integers (0=Mon, 1=Tue, ..., 6=Sun) - consistent with Python's weekday()
    # Using string values '0' to '6' to match HTML button data attributes in the template
    DAYS_OF_WEEK = [
        ("0", "M"),
        ("1", "T"),
        ("2", "W"),
        ("3", "T"),
        ("4", "F"),
        ("5", "S"),
        ("6", "S"),
    ]

    repeat = forms.ChoiceField(
        choices=REPEAT_CHOICES,
        label="Repeat",
        required=True,  # Make sure a choice is selected
        widget=forms.Select(
            attrs={
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 pr-4 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "id": "id_repeat_select",  # ID for JavaScript targeting
            }
        ),
    )

    # --- Add Start Date Field ---
    start_date = forms.DateField(
        label="Start Date",
        initial=datetime.date.today,  # Set initial value to today's date
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "type": "date",  # Use HTML5 date input
            },
        ),
    )
    # --- End Start Date Field ---

    at_time = forms.TimeField(
        label="At",
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={  # Use TimeInput for consistent format
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "placeholder": "HH:MM (e.g., 14:00)",
                "type": "time",  # Use HTML5 time input
            },
        ),
    )

    until_date = forms.DateField(
        label="Until",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={  # Use DateInput for consistent format
                "class": "mt-1 block w-full rounded-md border border-gray-300 p-2 focus:border-gray-500 focus:ring-gray-500 sm:text-sm",
                "placeholder": "YYYY-MM-DD (Optional)",  # Corrected placeholder
                "type": "date",  # Use HTML5 date input
            },
        ),
        required=False,  # End date is optional
    )

    # Hidden fields to store selections from JS widgets (weekly days, monthly dates)
    # Store weekly days as comma-separated integers (0-6)
    weekly_days = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "id_weekly_days_hidden"}), required=False
    )
    # Store monthly dates as comma-separated YYYY-MM-DD strings from Flatpickr
    monthly_dates = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "id_monthly_dates_hidden"}),
        required=False,
    )

    # --- Cleaning and Validation Methods ---

    def clean_weekly_days(self):
        """Validate weekly_days only if repeat is 'weekly'."""
        # Access cleaned_data to get the 'repeat' value which is processed first
        repeat = self.cleaned_data.get("repeat")
        weekly_days_str = self.cleaned_data.get("weekly_days")

        if repeat == "weekly":
            if not weekly_days_str:
                raise forms.ValidationError(
                    "Please select at least one day for weekly repetition."
                )
            # Validate format: comma-separated strings that are integers between 0 and 6
            try:
                # Split, filter out empty strings, convert to int, check range
                days = [int(d) for d in weekly_days_str.split(",") if d]
                if not all(0 <= day <= 6 for day in days):
                    raise forms.ValidationError(
                        "Invalid day number provided. Please select days from the options."
                    )
                # Return the original string after validation
                return weekly_days_str
            except (ValueError, TypeError):
                # Catch errors if splitting or converting to int fails
                raise forms.ValidationError("Invalid format for weekly days selected.")

        # If repeat is not weekly, we don't need to validate weekly_days.
        # It will be cleared in the main clean() method.
        return weekly_days_str  # Return whatever was submitted if not weekly

    def clean_monthly_dates(self):
        """Validate monthly_dates only if repeat is 'monthly'."""
        # Access cleaned_data to get the 'repeat' value
        repeat = self.cleaned_data.get("repeat")
        monthly_dates_str = self.cleaned_data.get("monthly_dates")

        if repeat == "monthly":
            if not monthly_dates_str:
                raise forms.ValidationError(
                    "Please select at least one date for monthly repetition."
                )
            # Validate format: comma-separated YYYY-MM-DD strings
            try:
                dates = []
                # Split, filter out empty strings, try parsing each date
                for date_str in monthly_dates_str.split(","):
                    if date_str:
                        try:
                            # Use strptime for parsing YYYY-MM-DD format
                            dates.append(
                                datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                            )
                        except ValueError:
                            # If any date string fails to parse, raise an error for this field
                            raise ValueError(f"Invalid date format: {date_str}")

                if not dates:  # Handle case where split resulted in no valid dates
                    raise forms.ValidationError(
                        "Please select at least one valid date for monthly repetition."
                    )

                # Optional additional validation: ensure selected dates are valid days of the month (1-31)
                # This might be redundant if Flatpickr only allows picking valid dates,
                # but adds robustness if input comes from elsewhere.
                # if not all(1 <= d.day <= 31 for d in dates):
                #      raise ValueError("Selected dates contain invalid day numbers for a month.")

                # Return the original string after validating all dates
                return monthly_dates_str
            except (ValueError, TypeError) as e:
                # Catch errors from strptime or general TypeErrors
                # Include the specific error message from ValueError for better debugging
                raise forms.ValidationError(f"Invalid date format selected: {e}")

        # If repeat is not monthly, we don't need to validate monthly_dates.
        # It will be cleared in the main clean() method.
        return monthly_dates_str  # Return whatever was submitted if not monthly

    def clean(self):
        """
        Processes the data from the hidden fields into usable formats (list of ints/dates)
        after individual field validation and performs cross-field validation.
        """
        cleaned_data = super().clean()
        repeat = cleaned_data.get("repeat")
        weekly_days_str = cleaned_data.get("weekly_days")
        monthly_dates_str = cleaned_data.get("monthly_dates")
        start_date = cleaned_data.get("start_date")
        until_date = cleaned_data.get("until_date")

        # --- Data Processing and Clearing ---
        # Process validated string data into lists and clear irrelevant data.
        # Store processed lists in new keys for clarity and easier use when creating models.

        # Initialize processed lists to empty
        cleaned_data["selected_week_days"] = []
        cleaned_data["selected_month_dates"] = []

        if repeat == "weekly":
            # Process weekly days if valid data exists
            if (
                weekly_days_str
            ):  # weekly_days_str is already validated by clean_weekly_days
                try:
                    # Convert comma-separated string '0,2,4' to list of integers [0, 2, 4]
                    cleaned_data["selected_week_days"] = sorted(
                        [int(d) for d in weekly_days_str.split(",") if d]
                    )
                except (ValueError, TypeError):
                    # This should ideally be caught in clean_weekly_days, but include defensively
                    self.add_error(
                        "weekly_days", "Internal error processing weekly days."
                    )
            # Clear monthly dates if weekly was selected
            cleaned_data["monthly_dates"] = None

        elif repeat == "monthly":
            # Process monthly dates if valid data exists
            if (
                monthly_dates_str
            ):  # monthly_dates_str is already validated by clean_monthly_dates
                try:
                    # Convert comma-separated string '2024-05-10,2024-05-25' to list of date objects
                    cleaned_data["selected_month_dates"] = sorted(
                        [
                            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                            for date_str in monthly_dates_str.split(",")
                            if date_str
                        ]
                    )
                except (ValueError, TypeError):
                    # This should ideally be caught in clean_monthly_dates, but include defensively
                    self.add_error(
                        "monthly_dates", "Internal error processing monthly dates."
                    )
            # Clear weekly days if monthly was selected
            cleaned_data["weekly_days"] = None

        else:  # repeat is 'daily' or 'Never' ('')
            # Clear both weekly and monthly data
            cleaned_data["weekly_days"] = None
            cleaned_data["monthly_dates"] = None
            # The processed lists will remain empty as initialized

        # --- Cross-field Validation ---
        if start_date and until_date and until_date < start_date:
            self.add_error(
                "until_date", "The end date cannot be before the start date."
            )

        # You might add more validation here, e.g.:
        # - If repeat is 'Never', ensure no weekly/monthly data was somehow submitted.
        # - Ensure 'at_time' is always required regardless of repeat type (it is currently).

        return cleaned_data


class ConfirmationForm(forms.Form):
    # This form might not have any fields, just used as a placeholder for a step
    pass
