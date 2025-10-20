from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path('setup-connection/', views.spotify_setup, name='spotify_setup'),
    path("top-tracks/", views.top_tracks, name="top_tracks"),
    path("top-artists/", views.top_artists, name="top_artists"),
    path("genre-cloud/", views.genre_cloud, name="genre_cloud"),
    path("profile/", views.profile_view, name="account_profile"),
    path("artist/<str:artist_id>/", views.artist_detail, name="artist_detail"),
]