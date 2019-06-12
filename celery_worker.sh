#!/bin/bash
celery -A events_hosting worker -l info
