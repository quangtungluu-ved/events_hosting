from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes

from django.db.models import Q

from events.models import Like, Participation, Comment, Event
from events.serializers import CommentSerializer, CommentBlockSerializer

from utils.permissions import CommentOwnerOnly


@api_view(['POST'])
def like_event(request, event_id):
    current_user = request.user
    try:
        saved_event = Event.objects.get(pk=event_id)
        if saved_event.like_set.filter(user=current_user.id).exists():
            saved_event.like_set.filter(user=current_user.id).delete()
            return Response({
                'like': True,
                'msg': f'remove like on event {saved_event.title}'})
        else:
            saved_event.like_set.add(Like(user=current_user), bulk=False)
            return Response({
                'like': False,
                'msg': f'like event {saved_event.title}'})
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def participate_event(request, event_id):
    current_user = request.user
    try:
        saved_event = Event.objects.get(pk=event_id)
        if saved_event.participation_set.filter(user=current_user).exists():
            saved_event.participation_set.filter(user=current_user).delete()
            return Response({
                'participate': False,
                'msg': f'Leave event {saved_event.title}'})
        else:
            concurent_participations = current_user.participation_set.filter(
                Q(event__start_date__lte=saved_event.start_date, event__end_date__gte=saved_event.start_date)
                |
                Q(event__start_date__gt=saved_event.start_date, event__start_date__lte=saved_event.end_date))
            concurent_events = list(map(
                lambda x: {'event_id': x.event.id, 'event_title': x.event.title},
                concurent_participations))
            saved_event.participation_set.add(
                Participation(user=current_user), bulk=False)
            return Response({
                'participate': True,
                'msg': f'Participate event {saved_event.title}',
                'concurent_events': concurent_events})
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_event(request, event_id):
    try:
        saved_event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        current_user = request.user
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=current_user, event=saved_event)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        offset = int(request.GET.get('offset', '0'))
        serializer = CommentBlockSerializer({
            'offset': offset,
            'event_id': saved_event.id,
            'comments': saved_event.comment_set.all()})
        return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([CommentOwnerOnly])
def edit_comment_event(request, event_id, comment_id):
    current_user = request.u200ser
    try:
        saved_comment = Comment.objects.get(pk=comment_id)
        serializer = CommentSerializer(
            instance=saved_comment,
            data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
