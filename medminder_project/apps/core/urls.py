from django.urls import path
from . import views
from .views import LandingPageView

app_name = "core"

urlpatterns = [
    # path('', LandingPageView.as_view(), name='landing_page'),
    path("", views.home, name="home"),  # Adjust to your view function
]
