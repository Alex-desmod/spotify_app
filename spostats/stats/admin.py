from django.contrib import admin
from .models import Profile, Play, Gig
from import_export import resources
from import_export.admin import ExportMixin

# Register your models here.
class GigResource(resources.ModelResource):
    class Meta:
        model = Gig


admin.site.register(Profile)
admin.site.register(Play)

@admin.register(Gig)
class GigAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = GigResource
    list_display = ['event_date', 'artist_name', 'venue', 'city']