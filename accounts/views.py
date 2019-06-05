from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from accounts.serializers import VisitorDetail, VisitorUpdate, VisitorCreate, Login
from django.contrib.auth import login as django_login, logout as django_logout
from accounts.decorators import class_view_authorize
from authentication.csrf import CsrfExemptSessionAuthentication


class LoginView(APIView):
    def post(self, request):
        user = User.objects.get(pk=1)
        django_login(request, user)
        return Response(status=status.HTTP_200_OK)


class LogoutView(APIView):
    @class_view_authorize
    def post(self, request):
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VisitorsView(APIView):
    @class_view_authorize
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        saved_visitors = User.objects.exclude(is_admin=True)
        serializers = VisitorDetail(saved_visitors, many=True)
        return Response(serializers.data)

    @class_view_authorize
    def post(self, request):
        serializer = VisitorCreate(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class VisitorView(APIView):
    @class_view_authorize
    def get(self, request, visitor_id):
        try:
            saved_vistor = User.objects.exclude(
                is_admin=True).get(pk=visitor_id)
            serializer = VisitorDetail(saved_vistor)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @class_view_authorize
    def put(self, request, visitor_id):
        try:
            saved_vistor = User.objects.exclude(
                is_admin=True).get(pk=visitor_id)
            serializer = VisitorUpdate(
                instance=saved_visitor,
                data=request.data,
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                saved_visitor = serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @class_view_authorize
    def delete(self, request, visitor_id):
        try:
            saved_vistor = User.objects.exclude(
                is_admin=True).get(pk=visitor_id)
            saved_vistor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
