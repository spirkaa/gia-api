import csv
import datetime
from io import StringIO

import pytest

EXAM_FILE = {
    "name": "2020-06-13__11__rab_ppe_test.xlsx",
    "url": "http://rcoi.com/2020-06-13__11__rab_ppe_test.xlsx",
    "size": "1024000",
    "last_modified": datetime.datetime(2020, 5, 15, 16, 23, 42),
}
EXAM_FILE_DIFF_DATE = EXAM_FILE.copy()
EXAM_FILE_DIFF_DATE.update({"last_modified": datetime.datetime(2020, 6, 1, 1, 1, 1)})

SAME_FILE_DIFF_DATE = [EXAM_FILE, EXAM_FILE_DIFF_DATE]

DIFF_FILES = [
    EXAM_FILE,
    {
        "name": "2020-06-14__11__rab_ppe_test.xlsx",
        "url": "http://rcoi.com/2020-06-14__11__rab_ppe_test.xlsx",
        "size": "2048000",
        "last_modified": datetime.datetime(2020, 5, 16, 0, 0, 0),
    },
]


@pytest.fixture
def exams_csv():
    """
    csv file
    """
    stream = StringIO()
    writer = csv.writer(stream, delimiter="\t", quotechar="'")
    writer.writerow(
        [
            "datafile",
            "date",
            "level",
            "ppe_code",
            "ppe_name",
            "ppe_addr",
            "position",
            "name",
            "organisation",
        ]
    )
    writer.writerow(
        [
            "2020-06-13__11__rab_ppe_test.xlsx",
            "2020-06-13",
            "11",
            "1000",
            "ppe",
            "addr",
            "pos",
            "employee",
            "org",
        ]
    )
    stream.seek(0)
    return stream


@pytest.fixture(params=[DIFF_FILES, SAME_FILE_DIFF_DATE])
def mocker_xlsx_to_csv(request, mocker, exams_csv):
    """
    mock of 'apps.rcoi.xlsx_to_csv'
    """
    mocker.patch("apps.rcoi.xlsx_to_csv.get_files_info", return_value=request.param)
    mocker.patch("apps.rcoi.xlsx_to_csv.download_file")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_stream", return_value=exams_csv)
    yield mocker
    mocker.resetall()


@pytest.fixture
def mocker_xlsx_to_csv_simple(mocker, exams_csv):
    """
    mock of 'apps.rcoi.xlsx_to_csv'
    """
    mocker.patch("apps.rcoi.xlsx_to_csv.get_files_info", return_value=[EXAM_FILE])
    mocker.patch("apps.rcoi.xlsx_to_csv.download_file")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_stream", return_value=exams_csv)
    yield mocker
    mocker.resetall()
