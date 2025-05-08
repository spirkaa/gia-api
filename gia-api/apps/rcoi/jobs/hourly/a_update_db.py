from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    """Parse xlsx from rcoi.mcko.ru and update database."""

    help = "Parse xlsx from rcoi.mcko.ru and update database."

    def execute(self):
        from apps.rcoi.models import RcoiUpdater

        RcoiUpdater().run()
