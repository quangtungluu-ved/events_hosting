from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token
from .models import Event, Comment, Channel, Image, Event_Channel
from events.tasks import notify_on_event_changes, schedule

# Register models from here.
admin.site.register(Channel)

admin.site.site_header = 'Event Hosting'


class ImageInline(admin.TabularInline):
    model = Image
    min_num = 0
    exclude = ('create_at'),
    extra = 1


class EventChannelInline(admin.TabularInline):
    model = Event_Channel
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_date', 'end_date', )
    fields = ('title', 'description', 'location', ('start_date', 'end_date'), )
    actions_on_top = False
    inlines = [
        ImageInline,
        EventChannelInline,
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()
            schedule(obj)
            return
        old_obj = Event.objects.get(pk=obj.pk)
        obj.save()
        if old_obj.start_date != obj.start_date \
            or old_obj.end_date != obj.end_date \
                or old_obj.location != obj.location:
            notify_on_event_changes.delay(obj.id)
        if old_obj.start_date != obj.start_date:
            schedule(obj)
