from __future__ import absolute_import, unicode_literals

from datetime import timedelta, datetime
from celery import shared_task
from events.models import Event
from services import mail as mail_service
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime


def clear_schedule(event):
    task_name = f'notify_before_start_event_{event.id}'
    PeriodicTask.objects.filter(name=task_name).delete()


def schedule(event):
    clear_schedule(event)
    notify_time = event.start_date - timedelta(hours=1)
    cron_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=notify_time.minute,
        hour=notify_time.hour,
        day_of_month=notify_time.day,
        month_of_year=notify_time.month,
        timezone=settings.TIME_ZONE)
    PeriodicTask.objects.create(
        crontab=cron_schedule,
        name=f'notify_before_start_event_{event.id}',
        task='events.tasks.notify_before_start',
        args=[event.id])


@shared_task
def notify_before_start(event_id):
    try:
        event = Event.objects.get(pk=event_id)
        if timezone.now() < event.start_date - timedelta(hours=1, minutes=5):
            return False
        if timezone.now() > event.start_date:
            clear_schedule(event)
            return False
        mail_service.events.notify_before_start(event)
        clear_schedule(event)
        return True
    except Event.DoesNotExist:
        clear_schedule(event)
        return False


@shared_task
def notify_on_event_changes(event_id):
    try:
        event = Event.objects.get(pk=event_id)
        mail_service.events.notify_on_changes(event)
        return True
    except Event.DoesNotExist:
        return False
