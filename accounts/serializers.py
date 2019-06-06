from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.models import User
from django.contrib.auth import authenticate as django_auth


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username', '')
        password = data.get('password', '')
        user = django_auth(username=username, password=password)
        data['user'] = user
        return data


class VisitorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class VisitorCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        validated_data['is_admin'] = 0
        validated_data['is_superuser'] = 0
        new_visitor = User.objects.create(**validated_data)
        new_visitor.set_password(validated_data.get('password'))
        new_visitor.save()
        return new_visitor


class VisitorUpdateSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            instance.set_password(validated_data.get('password'))
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
