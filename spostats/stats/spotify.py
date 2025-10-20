import time
from datetime import timedelta
import requests
from django.utils import timezone
from django.conf import settings
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

SPOTIFY_API = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

class SpotifyClient:
    def __init__(self, user):
        self.user = user
        try:
            self.account = SocialAccount.objects.get(user=user, provider="spotify")
        except SocialAccount.DoesNotExist:
            self.account = None
            self.token = None
            return

        try:
            self.token = SocialToken.objects.get(account=self.account)
        except SocialToken.DoesNotExist:
            self.token = None

    def _ensure_token(self):
        # refresh 5 minutes before the token expires
        if self.token.expires_at and self.token.expires_at <= timezone.now() + timedelta(minutes=5):
            self._refresh_token()

    def _refresh_token(self):
        app = SocialApp.objects.get(provider="spotify")
        # refresh_token may be saved in token.token_secret or in token.extra_data — we'll check both
        refresh_token = getattr(self.token, "token_secret", None) or (self.token.token_secret) \
                        or (self.token.extra_data or {}).get("refresh_token")
        if not refresh_token:
            return  # the first login could not return a refresh_token
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": app.client_id,
            "client_secret": app.secret,
        }
        r = requests.post(SPOTIFY_TOKEN_URL, data=data, timeout=10)
        r.raise_for_status()
        payload = r.json()
        self.token.token = payload["access_token"]
        # Spotify may return a new refresh_token — save it
        if "refresh_token" in payload:
            self.token.token_secret = payload["refresh_token"]
        if "expires_in" in payload:
            self.token.expires_at = timezone.now() + timedelta(seconds=payload["expires_in"])
        self.token.save()

    def _headers(self):
        self._ensure_token()
        return {"Authorization": f"Bearer {self.token.token}"}

    def get(self, path, params=None):
        r = requests.get(f"{SPOTIFY_API}{path}", headers=self._headers(), params=params or {}, timeout=15)
        if r.status_code == 401:
            # just in case - we try to update one more time and repeat
            self._refresh_token()
            r = requests.get(f"{SPOTIFY_API}{path}", headers=self._headers(), params=params or {}, timeout=15)
        r.raise_for_status()
        return r.json()

    # Useful methods:
    def me(self):
        return self.get("/me")

    def top_items(self, item_type="tracks", time_range="short_term", limit=20):
        return self.get(f"/me/top/{item_type}", params={"time_range": time_range, "limit": limit})

    def recently_played(self, after_ms=None, limit=50):
        params = {"limit": limit}
        if after_ms:
            params["after"] = after_ms
        return self.get("/me/player/recently-played", params=params)
