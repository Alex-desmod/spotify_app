from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.db import transaction

from stats.models import Play, Profile
from stats.spotify import SpotifyClient


class Command(BaseCommand):
    help = "Sync recently played tracks from Spotify API into DB"

    def handle(self, *args, **options):
        for profile in Profile.objects.select_related("user"):
            self.stdout.write(f"Syncing for {profile.user.email or profile.user.username}...")
            client = SpotifyClient(profile.user)

            try:
                data = client.recently_played(limit=50)
            except Exception as e:
                self.stderr.write(f"  Failed to fetch data for {profile.user}: {e}")
                continue

            items = data.get("items", [])
            if not items:
                self.stdout.write("  No new plays found.")
                continue

            plays_to_create = []
            for item in items:
                played_at = parse_datetime(item["played_at"])
                if played_at and not played_at.tzinfo:
                    played_at = make_aware(played_at)

                plays_to_create.append(
                    Play(
                        user=profile.user,
                        spotify_track_id=item["track"]["id"],
                        track_name=item["track"]["name"],
                        artist_name=", ".join([a["name"] for a in item["track"]["artists"]]),
                        played_at=played_at,
                        duration_ms=item["track"]["duration_ms"],
                    )
                )

            # bulk_create
            try:
                with transaction.atomic():
                    Play.objects.bulk_create(
                        plays_to_create,
                        ignore_conflicts=True,  # unique_together
                    )
            except Exception as e:
                self.stderr.write(f"  Bulk insert failed: {e}")
                continue

            self.stdout.write(f"  Synced {len(plays_to_create)} plays.")
