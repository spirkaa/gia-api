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


def test_rcoi_updater_exception_no_datasource():
    """
    Test - DB Updater fail
    """
    with pytest.raises(models.DataSource.DoesNotExist):
        assert models.RcoiUpdater().run()


def test_rcoi_updater(mocker, file_info, csv_data):
    """
    Test - DB Updater
    """
    G(models.DataSource)
    mocker.patch("apps.rcoi.xlsx_to_csv.get_files_info", return_value=file_info)
    mocker.patch("apps.rcoi.xlsx_to_csv.download_file")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_stream", return_value=csv_data)
    models.RcoiUpdater().run()

    exam = models.Exam.objects.count()
    assert exam == 1

    mocker.resetall()
