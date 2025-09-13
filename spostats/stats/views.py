from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from .spotify import SpotifyClient
from .models import Play, Profile
from collections import Counter

def _require_spotify(user):
    # if no connected Spotify account - forward to login
    from allauth.socialaccount.models import SocialAccount
    if not SocialAccount.objects.filter(user=user, provider="spotify").exists():
        return False
    return True


@login_required
def dashboard(request):
    if not _require_spotify(request.user):
        return redirect("/accounts/spotify/login/")
    client = SpotifyClient(request.user)
    profile = Profile.objects.get(user=request.user)
    top_tracks = client.top_items("tracks", "short_term", 10)["items"]
    recent = client.recently_played(limit=10)["items"]
    return render(request, "stats/dashboard.html", {
        "profile": profile,
        "top_tracks": top_tracks,
        "recent": recent,
    })

@login_required
def top_tracks(request):
    rng = request.GET.get("range", "short_term")
    client = SpotifyClient(request.user)
    data = client.top_items("tracks", rng, 20)["items"]
    return render(request, "stats/top_tracks.html", {"items": data, "rng": rng})

@login_required
def top_artists(request):
    rng = request.GET.get("range", "short_term")
    client = SpotifyClient(request.user)
    data = client.top_items("artists", rng, 20)["items"]
    return render(request, "stats/top_artists.html", {"items": data, "rng": rng})

@login_required
def recent(request):
    client = SpotifyClient(request.user)
    data = client.recently_played(limit=50)["items"]
    return render(request, "stats/recent.html", {"items": data})

@login_required
def genres(request):
    client = SpotifyClient(request.user)
    artists = client.top_items("artists", "short_term", 50)["items"]
    counts = Counter()
    for a in artists:
        for g in a.get("genres", []):
            counts[g] += 1
    # list (genre, weight) for our genres cloud
    items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:100]
    return render(request, "stats/genres.html", {"genres": items})

@login_required
def heatmap(request):
    # counting a number of Plays per day right in SQL
    qs = (
        Play.objects
        .filter(user=request.user)
        .annotate(day=TruncDate("played_at"))   # cutting time, leaving date only
        .values("day")
        .annotate(count=Count("id"))           # number of Plays per day
        .order_by("day")
    )

    # trasforming QuerySet in a dictionary { "YYYY-MM-DD": count }
    data = {row["day"].isoformat(): row["count"] for row in qs}

    return render(request, "stats/heatmap.html", {"data": data})