from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages # Import the messages framework
from django.urls import reverse
from django.conf import settings

from apps.core.forms import ReceiveUpdatesForm
from apps.accounts.models import ReceiveUpdates
# Create your views here.
class LandingPageView(TemplateView):
    template_name = "core/landing_page.html"

    def get(self, request, *args, **kwargs):
        # If the user is already authenticated, redirect them away from the landing page
        if request.user.is_authenticated:
            # Redirect to the URL specified in settings.LOGIN_REDIRECT_URL
            # Or directly to a known dashboard url name if preferred:
            # return redirect(reverse('reminders:dashboard')) # Adjust accounts/url name if needed
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request, *args, **kwargs)
    
def home (request):
    """
    Render the core page.
    """
    if request.method == 'POST':
            form = ReceiveUpdatesForm(request.POST)
            # Note: The form only validates the email field from POST data.
            # We handle the 'user' and 'notifications' fields manually below.

            if form.is_valid():
                email = form.cleaned_data['email']

                # --- Handle saving to the ReceiveUpdates model ---
                # Based on your model structure (OneToOneField to User),
                # we can only link this to a *logged-in* user.
                if not request.user.is_authenticated:
                    messages.error(request, "You must be logged in to sign up for updates.")
                    # Re-render with the form and error message
                    form = ReceiveUpdatesForm(initial={'email': email}) # Keep email in the form
                    return render(request, 'core/landing_page.html', {'form': form})

                # Check if an entry already exists for this logged-in user or this email
                # Since user is OneToOne and email is unique, checking either is sufficient for a logged-in user.
                # Checking by user is more direct due to OneToOne.
                existing_entry = ReceiveUpdates.objects.filter(user=request.user).first()
                # Alternatively, check by email (though user is primary key in this OneToOne context for uniqueness)
                # existing_entry_by_email = ReceiveUpdates.objects.filter(email=email).first()


                if existing_entry:
                    messages.info(request, "You are already on the updates list!")
                    # Optionally update the email if they submitted a different one, or just confirm
                    # if existing_entry.email != email:
                    #     existing_entry.email = email
                    #     existing_entry.save()
                    #     messages.success(request, "Updated your email for updates!")
                else:
                    # Create the new entry for the logged-in user
                    # The 'notifications' field defaults to True
                    ReceiveUpdates.objects.create(user=request.user, email=email, notifications=True)
                    messages.success(request, "Thank you for signing up for updates!")

                # Redirect to the same page or a success page after successful submission/handling
                # This prevents form resubmission on page refresh
                return redirect('landing_page') # Use the URL name defined in urls.py

            else:
                # Form is not valid (e.g., email format is wrong)
                # Errors are attached to the form object automatically
                messages.error(request, "Please enter a valid email address.")
                # Continue to render the page with the form containing errors

    else: # GET request
            # Create an empty form instance for displaying the form
            # If the user is logged in and already on the list, maybe pre-fill the email?
            initial_data = {}
            if request.user.is_authenticated:
                try:
                    existing_entry = ReceiveUpdates.objects.get(user=request.user)
                    initial_data['email'] = existing_entry.email
                    messages.info(request, "You are already signed up for updates!") # Inform them they are already signed up
                except ReceiveUpdates.DoesNotExist:
                    pass # User is logged in but not on the list yet


            form = ReceiveUpdatesForm(initial=initial_data)


     # Render the landing page template, passing the form to the context
    return render(request, 'core/landing_page.html', {'form': form})