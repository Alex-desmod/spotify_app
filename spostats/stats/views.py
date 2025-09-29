import json
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models.functions import TruncDate
from django.http import JsonResponse

from .spotify import SpotifyClient
from .models import Play, Profile
from .forms import ProfileForm
from collections import Counter


def _require_spotify(user):
    # if no connected Spotify account - forward to login
    from allauth.socialaccount.models import SocialAccount
    if not SocialAccount.objects.filter(user=user, provider="spotify").exists():
        return False
    return True

def _top_items(request, item_type="tracks"):
    client = SpotifyClient(request.user)

    # short_term by default
    time_range = request.GET.get("range", "short_term")
    show_all = request.GET.get("show") == "all"

    try:
        data = client.top_items(item_type=item_type, time_range=time_range, limit=50)
    except Exception:
        return redirect("account_login")

    items = []
    for obj in data.get("items", []):
        if item_type == "tracks":
            items.append({
                "name": obj["name"],
                "year": obj["album"]["release_date"][:4],
                "artist": ", ".join([a["name"] for a in obj["artists"]]),
                "album_cover": obj["album"]["images"][1]["url"] if obj["album"]["images"] else None,
            })
        else:  # artists
            items.append({
                "name": obj["name"],
                "genres": ", ".join(obj.get("genres", [])),
                "image": obj["images"][1]["url"] if obj.get("images") else None,
            })

    context = {
        "item_type": item_type,
        "time_range": time_range,
        "items": items[:50],  # limit just in case
        "show_all": show_all,
    }
    return render(request, f"stats/top_{item_type}.html", context)

@login_required
def dashboard(request):
    client = SpotifyClient(request.user)

    try:
        data = client.recently_played(limit=50)
    except Exception:
        # if something's wrong (for example the token is lost) → redirect to login
        return redirect("account_login")

    recent_tracks = []
    for item in data.get("items", []):
        track = item["track"]
        recent_tracks.append({
            "name": track["name"],
            "year": track["album"]["release_date"][:4],
            "artist": ", ".join([a["name"] for a in track["artists"]]),
            "album_cover": track["album"]["images"][1]["url"] if track["album"]["images"] else None,
            "played_at": item["played_at"],
        })

    return render(request, "stats/dashboard.html", {"recent_tracks": recent_tracks})

@login_required
def top_tracks(request):
    return _top_items(request, item_type="tracks")

@login_required
def top_artists(request):
    return _top_items(request, item_type="artists")

@login_required
def genre_cloud(request):
    client = SpotifyClient(request.user)

    try:
        data = client.top_items(item_type="artists", time_range="long_term", limit=50)
    except Exception:
        return redirect("account_login")

    genres = []
    for artist in data.get("items", []):
        genres.extend(artist.get("genres", []))

    counter = Counter(genres).most_common(50)  # list of (genre, count)

    # Size normalization in px range
    min_size, max_size = 12, 36
    genres_with_size = []
    if counter:
        counts = [c for _, c in counter]
        min_c, max_c = min(counts), max(counts)
        for genre, cnt in counter:
            if max_c == min_c:
                size = (min_size + max_size) // 2
            else:
                # linear normalization
                size = int(min_size + (cnt - min_c) * (max_size - min_size) / (max_c - min_c))
            genres_with_size.append({"name": genre, "count": cnt, "size": size})
    # if empty, genres_with_size is left empty

    return render(request, "stats/genre_cloud.html", {"genres": genres_with_size})

# @login_required
# def heatmap_view(request):
#     return render(request, "stats/heatmap.html")

# @login_required
# def heatmap_data(request):
#     # taking all plays of the current user
#     plays = (
#         Play.objects.filter(user=request.user)
#         .annotate(day=TruncDate("played_at"))
#         .values("day")
#         .annotate(count=Count("id"))
#         .order_by("day")
#     )
#
#     # cal-heatmap waits this format: {timestamp: count}
#     # timestamp = Unix epoch (UTC)
#     data = {}
#     for p in plays:
#         ts = int(datetime.datetime.combine(p["day"], datetime.time.min).timestamp())
#         data[ts] = p["count"]
#
#     return JsonResponse(data)

@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully ✅")
            return redirect("account_profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "account/profile.html", {"form": form})
