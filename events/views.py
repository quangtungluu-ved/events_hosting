from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes

from utils.permissions import AdminOrReadOnlyPermission, CommentOwnerOnly

from events.serializers import EventDetailSerializer, EventSerializer

from events.models import Event, Image, Like, Participation, Comment

from django.core.exceptions import ObjectDoesNotExist


class EventView(APIView):
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
            if serializer.is_valid():
                serializer.save()
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
            print(img.image.url)
        return Response(status=status.HTTP_202_ACCEPTED)


class EventsView(APIView):
    permission_classes = [AdminOrReadOnlyPermission]

    def get(self, request):
        saved_events = Event.objects.all()
        serializers = EventDetailSerializer(saved_events, many=True)
        return Response(serializers.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def like_event(request, event_id):
    current_user = request.user
    try:
        saved_event = Event.objects.get(pk=event_id)
        if saved_event.like_set.filter(user=current_user.id).exists():
            saved_event.like_set.filter(user=current_user.id).delete()
            return Response({'msg': 'unliked'})
        else:
            saved_event.like_set.add(Like(user=current_user), bulk=False)
            return Response({'msg': 'liked'})
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def participate_event(request, event_id):
    current_user = request.user
    try:
        saved_event = Event.objects.get(pk=event_id)
        if saved_event.participation_set.filter(user=current_user).exists():
            saved_event.participation_set.filter(user=current_user).delete()
            return Response({'msg': f'Left {saved_event.title}'})
        else:
            saved_event.participation_set.add(
                Participation(user=current_user), bulk=False)
            return Response({'msg': f'Participate {saved_event.title}'})
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def comment_event(request, event_id):
    curren_user = request.user
    try:
        saved_event = Event.objects.get(pk=event_id)
        saved_event.comment_set.add(
            Comment(user=curren_user, content=request.data.get('content', '')),
            bulk=False
        )
        return Response(status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([CommentOwnerOnly])
def edit_comment_event(request, event_id, comment_id):
    current_user = request.user
    try:
        saved_comment = Comment.objects.get(pk=comment_id)
        saved_comment.content = request.data.get(
            'content', saved_comment.content)
        saved_comment.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    except ObjectDoesNotExist:
        pass
