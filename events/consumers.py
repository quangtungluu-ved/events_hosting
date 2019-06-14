from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import async_to_sync

from .models import Event

import json


class EventViewConsumer(AsyncWebsocketConsumer):
    @classmethod
    def event_view_group(self, event_id):
        return 'event_view_%s_group' % event_id

    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.event_group_name = self.event_view_group(self.event_id)
        self.event = await get_event(self.event_id)
        if self.event:
            await self.channel_layer.group_add(
                self.event_group_name,
                self.channel_name)
            await self.accept()

    async def disconnect(self, clost_code):
        await self.channel_layer.group_discard(
            self.event_group_name,
            self.channel_name)

    async def update_event_like(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_like',
            'message': event['like']}))

    async def update_event_participants(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_participants',
            'message': event['participants']}))


class EventUpdateToChannel:
    channel_layer = get_channel_layer()

    @classmethod
    def update_like(self, event_id, like):
        async_to_sync(self.channel_layer.group_send)(
            EventViewConsumer.event_view_group(event_id),
            {
                'type': 'update_event_like',
                'like': like
            })

    @classmethod
    def update_participants(self, event_id, participants):
        async_to_sync(self.channel_layer.group_send)(
            EventViewConsumer.event_view_group(event_id),
            {
                'type': 'update_event_participants',
                'participants': participants
            })


@database_sync_to_async
def get_event(event_id):
    try:
        return Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return None
