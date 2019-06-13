# Generated by Django 2.2.2 on 2019-06-11 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20190611_1419'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['end_date'], name='events_even_end_dat_ef2904_idx'),
        ),
        migrations.RunSQL(
            ('CREATE FULLTEXT INDEX events_event_title_description_fulltext_index ON events_event(title, description, location)', ),
            ('DROP INDEX events_event_title_description_fulltext_index on events_event', ),
        )
    ]
