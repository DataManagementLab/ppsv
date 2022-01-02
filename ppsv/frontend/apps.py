"""Purpose of this file
This file configures the application for the frontend.
"""
from django.apps import AppConfig


class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'

