from django.core.management.base import BaseCommand
import logging
import os
from django.conf import settings
from ...cron import (
    send_reminders,
    generate_upcoming_reminder_logs,
    update_reminders,
    check_and_notify_streaks,
    check_and_notify_lost_streaks,
    check_and_notify_inactive_users,
)

# Configure logger to match cron.py (write to project root and console)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplication
logger.handlers = []

# Define formatter
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

# FileHandler to write to project_root/cron.log (one level above BASE_DIR)
project_root = os.path.dirname(settings.BASE_DIR)  # Parent of BASE_DIR
log_file = os.path.join(project_root, "cron.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info(f"Logging configured to write to {log_file} and console from run_cron_jobs")


class Command(BaseCommand):
    help = "Runs specified or all cron jobs for the MedMinder application"

    def add_arguments(self, parser):
        parser.add_argument(
            "--job",
            type=str,
            choices=[
                "send_reminders",
                "generate_upcoming_reminder_logs",
                "update_reminders",
                "check_and_notify_streaks",
                "check_and_notify_lost_streaks",
                "check_and_notify_inactive_users",
            ],
            help="Specify a single cron job to run. If omitted, all jobs are run.",
        )

    def handle(self, *args, **options):
        job = options.get("job")
        jobs_to_run = []

        if job:
            # Run only the specified job
            jobs_to_run = [(job, globals()[job])]
        else:
            # Run all jobs in order
            jobs_to_run = [
                ("send_reminders", send_reminders),
                ("generate_upcoming_reminder_logs", generate_upcoming_reminder_logs),
                ("update_reminders", update_reminders),
                ("check_and_notify_streaks", check_and_notify_streaks),
                ("check_and_notify_lost_streaks", check_and_notify_lost_streaks),
                ("check_and_notify_inactive_users", check_and_notify_inactive_users),
            ]

        for job_name, job_func in jobs_to_run:
            self.stdout.write(f"Running {job_name}...")
            logger.info(f"Starting {job_name} via management command")
            try:
                job_func()
                self.stdout.write(self.style.SUCCESS(f"Successfully ran {job_name}."))
                logger.info(f"Completed {job_name} successfully")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error in {job_name}: {e}"))
                logger.error(f"Error running {job_name}: {e}", exc_info=True)

        if not job:
            self.stdout.write(self.style.SUCCESS("All cron jobs completed."))
