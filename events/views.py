from events.apis import *

from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.utils.safestring import mark_safe

from events.models import Event


def view_event_detail(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
        event.like = event.like_set.count()
        event.participants = event.participation_set.count()
        return render(request, 'event/event.html', {'event': event})
    except Event.DoesNotExist:
        return HttpResponseNotFound()
