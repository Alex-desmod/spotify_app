from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=64, blank=True)
    display_name = models.CharField(max_length=255, blank=True)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return self.display_name or self.user.username

class Play(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spotify_track_id = models.CharField(max_length=64, db_index=True)
    track_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    played_at = models.DateTimeField(db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "spotify_track_id", "played_at")]
        ordering = ["-played_at"]

class Gig(models.Model):
    event_id = models.CharField(max_length=50, blank=True)
    event_date = models.DateField()
    artist_name = models.CharField(max_length=255)
    venue = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    url = models.URLField(blank=True)

    # many-to-many
    attendees = models.ManyToManyField(Profile, related_name="gigs", blank=True)

    def __str__(self):
        return f'{self.event_date} {self.artist_name}'

    class Meta:
        ordering = ["-event_date"]
        verbose_name = "Gig"
        verbose_name_plural = "Gigs"
        unique_together = [("event_date", "artist_name", "venue", "city", "country")]