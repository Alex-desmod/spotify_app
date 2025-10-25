import os
import requests

from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Gig
from .spotify import SpotifyClient
from .forms import ProfileForm

from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY")

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
                "id": obj["id"],
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
def spotify_setup(request):
    # Check if Spotify is connected
    has_spotify = SocialAccount.objects.filter(user=request.user, provider='spotify').exists()

    if has_spotify:
        # Alright, go to the dashboard
        return redirect('dashboard')

    # if Spotify is not connected — show the waiting page
    return render(request, "stats/setup_connection.html")

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
        data = client.top_items(item_type="artists", time_range="medium_term", limit=50)
    except Exception:
        return redirect("account_login")

    genres = []
    for artist in data.get("items", []):
        genres.extend(artist.get("genres", []))

    counter = Counter(genres).most_common(50)  # list of (genre, count)

    # Size normalization in px range
    min_size, max_size = 12, 42
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

@login_required
def artist_detail(request, artist_id):
    client = SpotifyClient(request.user)
    artist = client.get(f"/artists/{artist_id}")
    return JsonResponse(artist)

@login_required
def my_gigs(request):
    profile = request.user.profile
    gigs = profile.gigs.order_by("-event_date")
    return render(request, "stats/my_gigs.html", {"gigs": gigs})

@login_required
def add_gig(request):
    return render(request, "stats/add_gig.html")

@login_required
def import_setlistfm(request):
    if request.method == "POST":
        username = request.POST.get("setlistfm_username")
        headers = {
            "x-api-key": SETLISTFM_API_KEY,
            "Accept": "application/json",
        }

        all_gigs = []
        page = 1

        while True:
            url = f"https://api.setlist.fm/rest/1.0/user/{username}/attended?p={page}"
            response = requests.get(url, headers=headers)

            # API error — incorrect username or something else
            if response.status_code != 200:
                break

            data = response.json()
            setlists = data.get("setlist", [])

            # no pages left
            if not setlists:
                break

            all_gigs.extend(setlists)
            page += 1

            # just in case - to avoid an infinite cycle
            if page > 50:
                break

        if not all_gigs:
            return render(
                request,
                "stats/my_gigs.html",
                {"error_message": "No gigs found or wrong username"},
            )

        # saving gigs in the DB
        profile = request.user.profile
        for s in all_gigs:
            event_id = s.get("id")
            event_date_str = s.get("eventDate")
            artist_name = s.get("artist", {}).get("name")
            venue = s.get("venue", {}).get("name", "")
            city = s.get("venue", {}).get("city", {}).get("name", "")
            country = s.get("venue", {}).get("city", {}).get("country", {}).get("name", "")
            url = s.get("url", "")

            # converting date from "DD-MM-YYYY" to the datetime format
            try:
                event_date = datetime.strptime(event_date_str, "%d-%m-%Y").date()
            except Exception:
                event_date = None

            # if the gig exists — adding the user to the attendees
            gig, created = Gig.objects.get_or_create(
                event_id=event_id,
                defaults={
                    "event_date": event_date,
                    "artist_name": artist_name or "Unknown artist",
                    "venue": venue,
                    "city": city,
                    "country": country,
                    "url": url,
                },
            )

            gig.attendees.add(profile)

    return redirect("my_gigs")

