from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_page, name="signup"),  # Add the name='signup' here
    path("signup-user/", views.signup_user, name="signup_user"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("login-user/", views.login_user, name="login_user"),
    path("manage-plan/", views.manage_plan, name="manage_plan"),
    # path('profile/', views.profile, name='profile'),
    # path('invite-viewer/', views.invite_viewer, name='invite_viewer'),
]
