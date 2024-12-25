#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    if sys.argv[1] == 'runserver':
        # Set default host and port only for runserver command
        host = os.getenv('DJANGO_HOST', '127.0.0.1')
        port = os.getenv('DJANGO_PORT', '7000')
        execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
    else:
        # Use the provided command line arguments for other commands
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
