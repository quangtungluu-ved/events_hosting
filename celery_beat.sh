#!/bin/bash
celery -A events_hosting worker --beat --scheduler django --loglevel=info
