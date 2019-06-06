from rest_framework import serializers
from events.models import Event, Comment, Participation, Image

from django.conf import settings
from django.db.models import TextField
from django.utils.dateparse import parse_datetime


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        new_event = Event.objects.create(**validated_data)
        return new_event

    def update(self, instance, validated_data):
        instance.title = validated_data.get(
            'title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.location = validated_data.get(
            'location', instance.location)
        instance.start_date = validated_data.get(
            'start_date', instance.start_date)
        instance.end_date = validated_data.get(
            'end_date', instance.end_date)
        instance.save()
        return instance


class EventDetailSerializer(serializers.ModelSerializer):
    like = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'location',
            'start_date', 'end_date',
            'like', 'comments', 'participants', 'images',
        )

    def get_like(self, obj):
        return obj.like_set.count()

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        serializers = CommentSerializer(comments, many=True)
        return serializers.data

    def get_participants(self, obj):
        participations = obj.participation_set.all()
        serializers = ParticipantSerializer(participations, many=True)
        return [participant['username'] for participant in serializers.data]

    def get_images(self, obj):
        images = obj.image_set.all()
        serializers = ImageSerializer(images, many=True)
        return serializers.data


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'username', 'content', )

    def get_username(self, obj):
        return obj.user.username


class ParticipantSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = ('username', )

    def get_username(self, obj):
        return obj.user.username


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ('id', 'url', )

    def get_url(self, obj):
        return '{domain}{path}'.format(
            domain=settings.CURRENT_HOST,
            path=obj.image.url
        )
