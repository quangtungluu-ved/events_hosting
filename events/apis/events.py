from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes

from events.models import Event, Image, Event_Channel
from events.serializers import EventSerializer, EventDetailSerializer

from utils.permissions import AdminOrReadOnlyPermission

from services.mail.events import notify_on_changes


class EventView(APIView):
    permission_classes = [AdminOrReadOnlyPermission]

    def get(self, request, event_id):
        try:
            saved_event = Event.objects.get(pk=event_id)
            serializer = EventDetailSerializer(saved_event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, event_id):
        try:
            saved_event = Event.objects.get(pk=event_id)
            serializer = EventSerializer(instance=saved_event,
                                         data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                notify_on_changes(saved_event)
                return Response(serializer.data,
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        try:
            saved_event = Event.objects.get(pk=event_id)
            saved_event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EventImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AdminOrReadOnlyPermission]

    def put(self, request, event_id):
        try:
            saved_event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        uploaded_images = dict(request.data)['images']
        for image in uploaded_images:
            img = Image(event=saved_event)
            img.image.save(image.name, image)
        return Response(status=status.HTTP_202_ACCEPTED)


class SearchByKeyword:
    def __init__(self, queries):
        self.keywords = queries.get('keywords', '')
        self.keywords = list(filter(None, self.keywords.split(',')))

    def apply(self, query_set):
        keyword_queries = Q()
        for keyword in self.keywords:
            keyword_queries |= (Q(description__icontains=keyword)
                                | Q(title__icontains=keyword)
                                | Q(location__icontains=keyword))
        res = query_set
        res = res.filter(keyword_queries)
        return res


class Filter:
    def __init__(self, queries):
        self.start_date = queries.get('start_date', None)
        self.end_date = queries.get('end_date', None)
        self.channels = queries.get('channels', '').split(',')
        self.channels = list(filter(None, self.channels))
        self.page_offset = queries.get('page_offset', None)
        self.per_page = queries.get('per_page', None)
        if self.page_offset and self.per_page:
            self.page_offset = int(self.page_offset)
            self.per_page = int(self.per_page)

    def apply(self, query_set):
        res = query_set
        if self.start_date:
            res = res.exclude(end_date__lt=self.start_date)
        if self.end_date:
            res = res.exclude(start_date__gt=self.end_date)
        if len(self.channels) > 0:
            events_id = Event_Channel.objects.filter(
                channel__channel__in=self.channels
            ).values_list('event__id', flat=True).distinct()
            res = res.filter(id__in=events_id)
        if self.per_page is not None:
            offset = self.page_offset * self.per_page
            limit = self.per_page
            res = res[offset:offset+limit]
        return res


class EventsView(APIView):
    permission_classes = [AdminOrReadOnlyPermission]

    def get(self, request):
        saved_events = Event.objects.all()
        _filter = Filter(queries=request.GET)
        _search = SearchByKeyword(queries=request.GET)
        saved_events = _search.apply(saved_events)
        saved_events = _filter.apply(saved_events)
        serializers = EventDetailSerializer(saved_events, many=True)
        return Response(serializers.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
