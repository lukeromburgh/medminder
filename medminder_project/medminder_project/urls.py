"""
URL configuration for medminder_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),  # Include the URLs from the accounts app
    path('accounts/', include('apps.accounts.urls')),  # Include the URLs from the accounts app
    path('medminder/', include('apps.reminders.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('payments/', include('apps.payments.urls')),  # Include the URLs from the payments app
]
