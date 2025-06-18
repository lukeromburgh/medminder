from django.urls import path
from . import views
from .views import overview

app_name = 'documentation'

urlpatterns = [
    #path('', LandingPageView.as_view(), name='landing_page'),
    path('', views.overview, name='overview'),  # Adjust to your view function
]
