from django.contrib import admin
from .models import Profile, Play, Gig

# Register your models here.
admin.site.register(Profile)
admin.site.register(Play)
admin.site.register(Gig)