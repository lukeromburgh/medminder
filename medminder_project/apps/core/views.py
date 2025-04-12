from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings # To get LOGIN_REDIRECT_URL

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
    
def core (request):
    """
    Render the core page.
    """
    # This is a placeholder for the core page view
    # You can add your logic here
    return render(request, 'core/landing_page.html')