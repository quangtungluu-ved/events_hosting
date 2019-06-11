from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes

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
            return Response({'msg': 'removed like'})
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
            return Response({'msg': f'Left event {saved_event.title}'})
        else:
            saved_event.participation_set.add(
                Participation(user=current_user), bulk=False)
            return Response({'msg': f'Participate event {saved_event.title}'})
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
            'comments': saved_event.comment_set.all(),
        })
        return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([CommentOwnerOnly])
def edit_comment_event(request, event_id, comment_id):
    current_user = request.u200ser
    try:
        saved_comment = Comment.objects.get(pk=comment_id)
        serializer = CommentSerializer(
            instance=saved_comment,
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
