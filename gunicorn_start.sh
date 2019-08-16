#!/bin/bash
gunicorn events_hosting.wsgi:application --workers=4 --bind=0.0.0.0:8080
