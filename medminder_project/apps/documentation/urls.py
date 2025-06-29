from django.urls import path
from . import views
from .views import overview

app_name = "documentation"

urlpatterns = [
    # path('', LandingPageView.as_view(), name='landing_page'),
    path("", views.home, name="home"),  # Adjust to your view function
    path("overview", views.overview, name="overview"),  # Adjust to your view function
    path("the-why", views.the_why, name="the-why"),
    path("design-deep-dive", views.design_deep_dive, name="design-deep-dive"),
    path("under-the-hood", views.under_the_hood, name="under-the-hood"),
    path("strategy-plane", views.strategy_plane, name="strategy-plane"),
    path("scope-plane", views.scope_plane, name="scope-plane"),
    path("structure-plane", views.structure_plane, name="structure-plane"),
    path("skeleton-plane", views.skeleton_plane, name="skeleton-plane"),
    path("surface-plane", views.surface_plane, name="surface-plane"),
    path("user-stories", views.user_stories, name="user-stories"),
]
