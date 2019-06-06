from rest_framework.permissions import SAFE_METHODS, BasePermission

from events.models import Comment


class CommentOwnerOnly(BaseException):
    def has_permission(self, request, view):
        comment_id = view.kwargs['comment_id']
        comment = Comment.objects.get(pk=comment_id)
        return comment.user == request.user


class AdminOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin
