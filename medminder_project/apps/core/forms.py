# your_project/apps/core/forms.py

from django import forms
from apps.accounts.models import ReceiveUpdates

class ReceiveUpdatesForm(forms.ModelForm):
    class Meta:
        model = ReceiveUpdates
        # We only need the email field from the user input
        fields = ['email']
        # Add widgets for better HTML styling/placeholders
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-input px-4 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        }
        # You can also customize labels if needed
        labels = {
            'email': '', # Hide the label as placeholder is used
        }

    # Optional: Add custom validation if needed
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     # Add extra checks here if needed
    #     return email