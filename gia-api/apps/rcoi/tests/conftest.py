import csv
import datetime
from io import StringIO
from pathlib import Path

import pytest
from django.http import HttpResponse

from apps.rcoi import xlsx_to_csv

EXAM_FILE = {
    "name": "2020-06-13__11__.xlsx",
    "url": "http://rcoi.mcko.ru/2020-06-13__11__rab_ppe_test.xlsx",
    "size": "1024000",
    "last_modified": datetime.datetime(2020, 5, 15, 16, 23, 42),
}
EXAM_FILE_DIFF_DATE = EXAM_FILE.copy()
EXAM_FILE_DIFF_DATE.update({"last_modified": datetime.datetime(2020, 6, 1, 1, 1, 1)})

SAME_FILE_DIFF_DATE = [EXAM_FILE, EXAM_FILE_DIFF_DATE]

DIFF_FILES = [
    EXAM_FILE,
    {
        "name": "2020-06-14__11__.xlsx",
        "url": "http://rcoi.mcko.ru/2020-06-14__11__rab_ppe_test.xlsx",
        "size": "2048000",
        "last_modified": datetime.datetime(2020, 5, 16, 0, 0, 0),
    },
]


@pytest.fixture
def xlsx_file(settings):
    filename = "2020-06-13__11__.xlsx"
    return Path(settings.APPS_DIR) / "rcoi" / "tests" / "xlsx" / filename


@pytest.fixture(
    params=[
        "2020-06-13__11__bad_missing_column.xlsx",
        "2020-06-13__11__bad_missing_data.xlsx",
        "2020-06-13__11__bad_many_data_sheets.xlsx",
    ],
)
def xlsx_file_bad(settings, request):
    return Path(settings.APPS_DIR) / "rcoi" / "tests" / "xlsx" / request.param


@pytest.fixture
def xlsx_data(xlsx_file):
    # TODO: replace loading from xlsx file to generated data
    return xlsx_to_csv.load_sheet_data(xlsx_file)


@pytest.fixture
def csv_headers():
    return [
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


@pytest.fixture
def csv_data_row():
    return [
        "2020-06-13__11__.xlsx",
        "2020-06-13",
        "11",
        "1000",
        "ppe",
        "addr",
        "pos",
        "employee",
        "org",
    ]


@pytest.fixture
def exam_file():
    return EXAM_FILE


@pytest.fixture
def exam_file_diff_date():
    return EXAM_FILE_DIFF_DATE


@pytest.fixture
def exams_csv(csv_headers, csv_data_row):
    """
    csv file
    """
    stream = StringIO()
    writer = csv.writer(stream, delimiter="\t", quotechar="'")
    writer.writerow(csv_headers)
    writer.writerow(csv_data_row)
    stream.seek(0)
    return stream


@pytest.fixture
def mocker_xlsx_to_csv(mocker, exams_csv):
    """
    mock of 'apps.rcoi.xlsx_to_csv'
    """
    mocker.patch("apps.rcoi.xlsx_to_csv.get_files_info", return_value=DIFF_FILES)
    mocker.patch("apps.rcoi.xlsx_to_csv.download_file")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_stream", return_value=exams_csv)
    yield mocker
    mocker.resetall()


@pytest.fixture
def mocker_xlsx_to_csv_single_file(mocker, exams_csv):
    """
    mock of 'apps.rcoi.xlsx_to_csv'
    """
    mocker.patch("apps.rcoi.xlsx_to_csv.get_files_info", return_value=[EXAM_FILE])
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
    mocker.patch("apps.rcoi.xlsx_to_csv.prepare_file_info", return_value=EXAM_FILE)
    mocker.patch("apps.rcoi.xlsx_to_csv.download_file")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_csv")
    mocker.patch("apps.rcoi.xlsx_to_csv.save_to_stream", return_value=exams_csv)
    yield mocker
    mocker.resetall()


@pytest.fixture
def mocker_parse_sheet_data(mocker, csv_data_row):
    mocker.patch("apps.rcoi.xlsx_to_csv.load_sheet_data", return_value=["OK"])
    mocker.patch("apps.rcoi.xlsx_to_csv.parse_sheet_data", return_value=[csv_data_row])
    yield mocker
    mocker.resetall()


@pytest.fixture
def mocker_rcoi_updater(mocker):
    """
    mock of 'apps.rcoi.models.RcoiUpdater'
    """
    mocker.patch("apps.rcoi.models.RcoiUpdater.__init__", return_value=None)
    mocker.patch("apps.rcoi.models.RcoiUpdater.data", None, create=True)
    yield mocker
    mocker.resetall()


@pytest.fixture
def mocker_exam_importer(mocker):
    """
    mock of 'apps.rcoi.models.RcoiUpdater'
    """
    mocker.patch("apps.rcoi.models.ExamImporter.__init__", return_value=None)
    mocker.patch("apps.rcoi.models.ExamImporter.data", None, create=True)
    yield mocker
    mocker.resetall()


@pytest.fixture(params=[True, False])
def mocker_path(request, mocker):
    """
    mock of 'Path' parts
    """
    mocker.patch.object(Path, "exists", return_value=request.param)
    mocker.patch.object(Path, "mkdir")
    yield mocker
    mocker.resetall()


def _max_age_resp():
    return HttpResponse()


def _max_age_resp_with_header():
    r = HttpResponse()
    r["cache-control"] = "max-age=1200"
    return r


@pytest.fixture(params=[_max_age_resp(), _max_age_resp_with_header()])
def max_age_response(request):
    """
    response with and without header
    """
    return request.param
