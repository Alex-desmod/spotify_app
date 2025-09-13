from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("top/tracks/", views.top_tracks, name="top_tracks"),
    path("top/artists/", views.top_artists, name="top_artists"),
    path("recent/", views.recent, name="recent"),
    path("genres/", views.genres, name="genres"),
    path("heatmap/", views.heatmap, name="heatmap"),
]