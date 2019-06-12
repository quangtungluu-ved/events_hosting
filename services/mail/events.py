from events.models import Event
from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils.timezone import localtime


def notify_on_changes(event):
    participant_emails = list(event.participation_set.values_list(
        'user__email',
        flat=True
    ))
    subject = f'Update information on event {event.title}'
    message = f'{event.description}\n'
    message += f'{event.title} will be from {localtime(event.start_date)} to {localtime(event.end_date)}\n'
    message += f'Location: {event.location}\n'
    message += 'Regards,'
    datatuple = ((subject, message, settings.EMAIL_HOST_USER, [email])
                 for email in participant_emails)
    send_mass_mail(datatuple)


def notify_before_start(event):
    participant_emails = list(event.participation_set.values_list(
        'user__email',
        flat=True
    ))
    subject = f'Event {event.title} will start in 1 hour'
    message = f'Dear my friend,\n'
    message += f'{event.title} will start in 1 hour.\n'
    message += f'Join us to have fun\n'
    datatuple = ((subject, message, settings.EMAIL_HOST_USER, [email])
                 for email in participant_emails)
    send_mass_mail(datatuple)
