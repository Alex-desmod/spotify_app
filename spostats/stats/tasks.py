import datetime
from .models import Play
from .spotify import SpotifyClient

def sync_recently_played(user, limit=50):
    """taking the latest plays and writing them into Play"""
    client = SpotifyClient(user)
    data = client.recently_played(limit=limit)

    new_items = 0
    for item in data.get("items", []):
        track = item["track"]
        played_at = datetime.datetime.fromisoformat(
            item["played_at"].replace("Z", "+00:00")
        )

        # making a record if it doesn't exist
        obj, created = Play.objects.get_or_create(
            user=user,
            spotify_track_id=track["id"],
            played_at=played_at,
            defaults={
                "track_name": track["name"],
                "artist_name": ", ".join([a["name"] for a in track["artists"]]),
                "duration_ms": track.get("duration_ms"),
            }
        )
        if created:
            new_items += 1

    return new_items
