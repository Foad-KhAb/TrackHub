import os
import sys

def main():
    # Point to your settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_base.settings")
    # Hand off to Django's CLI
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
