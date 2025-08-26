from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from .models import Profile

@receiver(user_logged_in)
def sync_spotify_profile(request, user, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=user)
    sa = SocialAccount.objects.filter(user=user, provider="spotify").first()
    if not sa:
        return
    data = sa.extra_data or {}
    profile.spotify_id = data.get("id") or profile.spotify_id
    profile.display_name = data.get("display_name") or profile.display_name
    images = data.get("images") or []
    if images:
        profile.avatar_url = images[0].get("url") or profile.avatar_url
    profile.save()