from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token

from .models import Event, Comment, Channel, Image

from services.mail.events import notify_on_changes


# Register models from here.
admin.site.register(Channel)

admin.site.site_header = 'Event Hosting'


class ImageInline(admin.TabularInline):
    model = Image
    min_num = 0
    exclude = ('create_at'),


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_date', 'end_date', )
    fields = ('title', 'description', 'location', ('start_date', 'end_date'), )
    actions_on_top = False
    inlines = [ImageInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()
            return
        old_obj = Event.objects.get(pk=obj.pk)
        obj.save()
        if old_obj.start_date != obj.start_date \
            or old_obj.end_date != obj.end_date \
                or old_obj.location != obj.location:
            notify_on_changes(obj)
