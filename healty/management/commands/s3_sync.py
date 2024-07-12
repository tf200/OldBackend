import os

from django.core.management.base import BaseCommand
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class Command(BaseCommand):
    help = 'Sync local assets & media files to S3'

    def handle(self, *args, **options):
        storage = S3Boto3Storage()
        
        # Sync media files
        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                remote_path = os.path.relpath(local_path, settings.MEDIA_ROOT)
                with open(local_path, 'rb') as f:
                    self.stdout.write(f'Syncing {local_path} to {remote_path}')
                    storage.save(remote_path, f)
        self.stdout.write(self.style.SUCCESS('Media files synced to S3'))

        # Sync static files
        for dirpath, dirnames, filenames in os.walk(settings.STATIC_ROOT):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                remote_path = os.path.relpath(local_path, settings.STATIC_ROOT)
                with open(local_path, 'rb') as f:
                    self.stdout.write(f'Syncing {local_path} to {remote_path}')
                    storage.save(remote_path, f)
        self.stdout.write(self.style.SUCCESS('Static files synced to S3'))
