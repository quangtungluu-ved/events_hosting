from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.conf import settings


class BaseModel(models.Model):
    create_at = models.DateTimeField(default=timezone.localtime)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)

    def __str__(self):
        return self.title


class Channel(BaseModel):
    channel = models.CharField(max_length=50)


class Event_Channel(BaseModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['channel', 'event']


class Comment(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    content = models.CharField(max_length=250)

    def __str__(self):
        return self.content


class Like(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'event']


class Participation(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'event']


class Image(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
