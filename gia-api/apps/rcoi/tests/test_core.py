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


def test_rcoi_updater_same_file(mocker_xlsx_to_csv_single_file, exam_file):
    """
    Test - DB Updater - must process update because last_modified field for file is different
    """

    exam_file_diff_date = exam_file.copy()
    exam_file_diff_date.update(
        {"last_modified": datetime.datetime(2020, 6, 1, 1, 1, 1)}
    )

    G(models.DataSource)
    G(models.DataFile, modified=datetime.datetime(2019, 1, 1), **exam_file_diff_date)

    models.RcoiUpdater().run()
    exam_count = models.Exam.objects.count()
    assert exam_count == 1


def test_rcoi_updater_same_file_fail(mocker_xlsx_to_csv_single_file, exam_file):
    """
    Test - DB Updater - must fail when trying to process the same file within 5 minutes range
    """

    exam_file_diff_date = exam_file.copy()
    exam_file_diff_date.update(
        {"last_modified": datetime.datetime(2020, 6, 1, 1, 1, 1)}
    )

    G(models.DataSource)
    G(models.DataFile, **exam_file_diff_date)

    with pytest.raises(NotImplementedError):
        assert models.RcoiUpdater().run()


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
    mocker.resetall()


def test_rcoi_updater_if_data_is_none(mocker_rcoi_updater):
    """
    Test - DB Updater - data is None ('if' branch coverage)
    """
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
    mocker.resetall()


def test_exam_importer(mocker_xlsx_to_csv_simple, exam_file_diff_date):
    """
    Test - Exam Importer
    """
    exam_url = "http://123"
    exam_date = datetime.date(2020, 6, 1)
    exam_level = "123"

    # no file
    r1 = models.ExamImporter(exam_url, exam_date, exam_level)
    assert len(r1.data) == 9

    # same file
    r2 = models.ExamImporter(exam_url, exam_date, exam_level)
    assert r2.data is None

    # updated file
    mocker_xlsx_to_csv_simple.patch(
        "apps.rcoi.xlsx_to_csv.get_file_info", return_value=exam_file_diff_date
    )
    r3 = models.ExamImporter(exam_url, exam_date, exam_level)
    # print(r3)
    assert (
        len(r3.data) == 0
    )  # because of mocker, stream stays at the end after first read
