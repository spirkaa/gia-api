import csv
import datetime
from io import StringIO

import pytest


@pytest.fixture
def file_info():
    """
    mock value of 'apps.rcoi.xlsx_to_csv.get_files_info'
    """
    data = [
        {
            "name": "2020-06-13__11__rab_ppe_test.xlsx",
            "url": "http://rcoi.com/file.xlsx",
            "size": "1024000",
            "last_modified": datetime.datetime(2020, 5, 15, 16, 23, 42),
        }
    ]
    return data


@pytest.fixture
def csv_data():
    """
    mock value of 'apps.rcoi.xlsx_to_csv.save_to_stream'
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
