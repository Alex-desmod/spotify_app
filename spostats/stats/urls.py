from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("top-tracks/", views.top_tracks, name="top_tracks"),
    path("top-artists/", views.top_artists, name="top_artists"),
    path("genre-cloud/", views.genre_cloud, name="genre_cloud"),
    path("heatmap/", views.heatmap, name="heatmap"),
    path("profile/", views.profile_view, name="account_profile"),
]