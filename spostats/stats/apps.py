from django.apps import AppConfig


class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stats'

    def ready(self):
        from . import signals  # noqa

        # Monkey-patch allauth's Spotify adapter to use Bearer header
        # instead of the deprecated query-parameter auth method.
        # Allauth passes token as ?access_token=... which Spotify no longer accepts.
        from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
        from allauth.socialaccount.adapter import get_adapter

        def patched_complete_login(self, request, app, token, **kwargs):
            extra_data = (
                get_adapter()
                .get_requests_session()
                .get(self.profile_url, headers={"Authorization": f"Bearer {token.token}"})
            )
            extra_data.raise_for_status()
            return self.get_provider().sociallogin_from_response(
                request, extra_data.json()
            )

        SpotifyOAuth2Adapter.complete_login = patched_complete_login
