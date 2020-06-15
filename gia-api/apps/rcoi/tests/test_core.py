import datetime

import pytest
from ddf import G

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_send_subscriptions(mailoutbox):
    """
    Test - Send Subscriptions
    """
    employee = "test username"
    emp = G(models.Employee, name=employee)
    user = G(models.User)
    G(
        models.Exam, employee=emp,
    )
    G(
        models.Subscription, user=user, employee=emp,
    )

    models.send_subscriptions()

    assert len(mailoutbox) == 1
    assert user.email in mailoutbox[0].to
    assert emp.name in mailoutbox[0].body


def test_send_subscriptions_when_already_sent(mailoutbox):
    """
    Test - Send Subscriptions when already sent
    """
    employee = "test username"
    emp = G(models.Employee, name=employee)
    user = G(models.User)
    G(
        models.Exam, employee=emp,
    )
    G(
        models.Subscription,
        user=user,
        employee=emp,
        last_send=datetime.datetime(2035, 1, 1),
    )

    models.send_subscriptions()
    assert len(mailoutbox) == 0


def test_send_subscriptions_when_no_subs(mailoutbox):
    """
    Test - Send Subscriptions when no subs
    """
    models.send_subscriptions()
    assert len(mailoutbox) == 0


def test_rcoi_updater(mocker_xlsx_to_csv):
    """
    Test - DB Updater
    """
    G(models.DataSource)

    # Create an "updated" datafile with "old" exam for cleanup method (must delete exam)
    updated_datafile = G(models.DataFile)
    old_exam_in_updated_datafile = G(
        models.Exam,
        datafile=updated_datafile,
        created=datetime.datetime(2019, 1, 1),
        modified=datetime.datetime(2019, 1, 1),
    )
    # Create an "old" datafile with "old" exam for cleanup method (must skip exam)
    old_exam_in_old_datafile = G(
        models.Exam,
        created=datetime.datetime(2019, 1, 1),
        modified=datetime.datetime(2019, 1, 1),
        datafile__created=datetime.datetime(2019, 1, 1),
        datafile__modified=datetime.datetime(2019, 1, 1),
    )

    models.RcoiUpdater().run()

    # assertions for cleanup method
    assert not models.Exam.objects.filter(pk=old_exam_in_updated_datafile.id).exists()
    assert models.Exam.objects.filter(pk=old_exam_in_old_datafile.id).exists()

    # +2 from G() +1 from run() -1 from cleanup = 2
    exam_count = models.Exam.objects.count()
    assert exam_count == 2

    # Second Run with the same data for branch coverage
    models.RcoiUpdater().run()
    exam_count = models.Exam.objects.count()
    assert exam_count == 2


def test_rcoi_updater_exception_no_datasource(mocker_xlsx_to_csv_simple):
    """
    Test - DB Updater fail
    """
    with pytest.raises(models.DataSource.DoesNotExist):
        assert models.RcoiUpdater().run()


def test_rcoi_updater_if_tmp_path_exists(mocker_xlsx_to_csv_simple, mocker):
    """
    Test - DB Updater - tmp_path exists ('if' branch coverage)
    """
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("shutil.rmtree")

    G(models.DataSource)
    models.RcoiUpdater().run()
    exam_count = models.Exam.objects.count()
    assert exam_count == 1


def test_rcoi_updater_if_data_is_none(mocker):
    """
    Test - DB Updater - data is None ('if' branch coverage)
    """
    mocker.patch("apps.rcoi.models.RcoiUpdater.__init__", lambda x: None)
    mocker.patch("apps.rcoi.models.RcoiUpdater.data", None, create=True)

    models.RcoiUpdater().run()
    exam_count = models.Exam.objects.count()
    assert exam_count == 0


def test_rcoi_updater_if_data_is_bad(mocker):
    """
    Test - DB Updater - data is bad ('except' branch coverage)
    """
    mocker.patch("apps.rcoi.models.RcoiUpdater.__init__", lambda x: None)
    mocker.patch("apps.rcoi.models.RcoiUpdater.data", "unexpected_data", create=True)

    with pytest.raises(Exception):
        models.RcoiUpdater().run()
