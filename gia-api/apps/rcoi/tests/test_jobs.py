from apps.rcoi.jobs.hourly import send_subscriptions, update_db


def test_job_send_subscriptions(mocker):
    """
    Test - Job - Send subscriptions
    """
    mocker.patch("apps.rcoi.models.send_subscriptions")
    send_subscriptions.Job().execute()
    mocker.resetall()
    assert True


def test_job_update_db(mocker_rcoi_updater):
    """
    Test - Job - Update db
    """
    update_db.Job().execute()
    assert True
