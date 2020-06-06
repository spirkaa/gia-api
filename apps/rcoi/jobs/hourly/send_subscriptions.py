from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = "Send mail subscriptions"

    def execute(self):
        from apps.rcoi.models import send_subscriptions

        send_subscriptions()
        return
