from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, PeriodicTasks


class Command(BaseCommand):
    help = "Refresh Celery Beat tasks"

    def handle(self, *args, **options):
        # Disable all periodic tasks and reset last run time
        PeriodicTask.objects.update(enabled=False, last_run_at=None)
        self.stdout.write("Disabled all periodic tasks.")

        # Update changed periodic tasks
        PeriodicTasks.update_changed()
        self.stdout.write("Updated changed periodic tasks.")

        # Enable all periodic tasks
        PeriodicTask.objects.update(enabled=True)
        self.stdout.write("Enabled all periodic tasks.")

        # Update changed periodic tasks again
        PeriodicTasks.update_changed()
        self.stdout.write("Updated changed periodic tasks again.")
