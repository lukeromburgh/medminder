from django.urls import path
from . import views
from .views import overview

app_name = 'documentation'

urlpatterns = [
    #path('', LandingPageView.as_view(), name='landing_page'),
    path('', views.home, name='home'),  # Adjust to your view function
    path('overview', views.overview, name='overview'),  # Adjust to your view function
    path('the-why', views.the_why, name='the_why'),
    path('under-the-hood', views.under_the_hood, name='under_the_hood'),
]
