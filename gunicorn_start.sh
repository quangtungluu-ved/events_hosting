#!/bin/bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn events_hosting.wsgi:application --workers=4 --bind=0.0.0.0:8080
