from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from accounts.models import User
from accounts.serializers import \
    VisitorDetailSerializer, VisitorUpdateSerializer, \
    VisitorCreateSerializer, LoginSerializer

from services.oauth2.google import oauth2 as oauth2_google

from rest_framework_jwt.settings import api_settings


@api_view(['GET'])
def test_access(request):
    return Response('accessed')


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        token = api_settings.JWT_ENCODE_HANDLER(payload)
        return Response({
            **payload,
            'token': token,
            'exp': settings.JWT_AUTH['JWT_EXPIRATION_DELTA'].total_seconds()})


class VisitorsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        saved_visitors = User.objects.exclude(is_admin=True)
        serializers = VisitorDetailSerializer(saved_visitors, many=True)
        return Response(serializers.data)

    def post(self, request):
        serializer = VisitorCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VisitorView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, visitor_id):
        try:
            saved_vistor = User.objects.filter(
                is_admin=False).get(pk=visitor_id)
            serializer = VisitorDetailSerializer(saved_vistor)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, visitor_id):
        try:
            saved_visitor = User.objects.filter(
                is_admin=False).get(pk=visitor_id)
            serializer = VisitorUpdateSerializer(
                instance=saved_visitor,
                data=request.data,
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                saved_visitor = serializer.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, visitor_id):
        try:
            saved_vistor = User.objects.filter(
                is_admin=False).get(pk=visitor_id)
            saved_vistor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_google(request):
    return oauth2_google(request)
