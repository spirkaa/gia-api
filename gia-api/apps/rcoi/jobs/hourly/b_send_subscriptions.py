from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    """Send email with updates in user subscriptions."""

    help = "Send email with updates in user subscriptions."

    def execute(self):
        from apps.rcoi.models import send_subscriptions

        send_subscriptions()
