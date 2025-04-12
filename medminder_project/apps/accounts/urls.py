from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_page, name='signup'),  # Add the name='signup' here
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('profile/', views.profile, name='profile'),
    # path('invite-viewer/', views.invite_viewer, name='invite_viewer'),
]