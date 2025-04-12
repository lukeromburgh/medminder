from django.urls import path
from . import views
from .views import LandingPageView

urlpatterns = [
    #path('', LandingPageView.as_view(), name='landing_page'),
    path('', views.core, name='core'),  # Adjust to your view function
]
