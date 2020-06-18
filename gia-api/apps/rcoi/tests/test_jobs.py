from apps.rcoi.jobs.hourly import a_update_db, b_send_subscriptions


def test_job_send_subscriptions(mocker):
    """
    Test - Job - Send subscriptions
    """
    mocker.patch("apps.rcoi.models.send_subscriptions")
    b_send_subscriptions.Job().execute()
    mocker.resetall()
    assert True


def test_job_update_db(mocker_rcoi_updater):
    """
    Test - Job - Update db
    """
    a_update_db.Job().execute()
    assert True
