#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_settings.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    host = os.getenv('DJANGO_HOST', '127.0.0.1')  # Default to 0.0.0.0 if not set
    port = os.getenv('DJANGO_PORT', '7000')  # Default to 8000 if not set
    execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])


if __name__ == '__main__':
    main()
