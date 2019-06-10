import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login as django_login, logout as django_logout
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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
def oauth_google(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    redirect_uri = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI
    scope = 'email%20profile%20openid'
    if 'code' not in request.GET:
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                    '&client_id={}&redirect_uri={}&scope={}').format(
                        client_id,
                        redirect_uri,
                        scope)
        return redirect(auth_uri)
    else:
        auth_code = request.GET.get('code')
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        resp = requests.post(
            url='https://www.googleapis.com/oauth2/v4/token',
            data=data
        )
        print(resp.text)
        return redirect("/admin")
