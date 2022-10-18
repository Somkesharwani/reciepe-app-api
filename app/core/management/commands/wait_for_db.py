'''
Django command to wait or the DB to be available
'''

from dataclasses import dataclass
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command wait for Database"""

    def handle(self, *args, **options):
        """EntryPoint for command"""
        self.stdout.write('Waiting for Databases')
        db_up=False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up=True
            except(Psycopg2Error,OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
        #return super().handle(*args, **options)
