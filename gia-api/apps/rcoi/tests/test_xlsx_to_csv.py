import csv
import os
from datetime import date, datetime

import pytest
import responses

from apps.rcoi import xlsx_to_csv


def test_get_file_info():
    """
    Test Parser - Get File Info
    """
    url = "http://rcoi.mcko.ru/"
    filename = "rab_ppe_test.xlsx"
    exam_url = url + filename
    exam_date = date(2020, 6, 1)
    exam_level = "11"
    size = "1024000"
    last_modified = "Fri, 15 May 2020 16:23:42 GMT"
    lm_dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")

    responses.add(
        responses.HEAD,
        exam_url,
        headers={"Content-Length": size, "Last-Modified": last_modified},
    )

    r = xlsx_to_csv.get_file_info(exam_url, exam_date, exam_level)
    assert r["name"] == f"{exam_date}__{exam_level}__{filename}"
    assert r["size"] == size
    assert r["last_modified"] == lm_dt
    assert r["url"] == exam_url


@pytest.mark.parametrize("level", ["oge", "ege", "wtf"])
def test_get_files_info(level):
    """
    Test Parser - Get Files Info
    """
    url = "http://rcoi.mcko.ru/"
    filename = "rab_ppe_test.xlsx"
    fmt_url = f"{url}{level}/"
    file_url = f"{fmt_url}{filename}"
    size = "1024000"
    last_modified = "Fri, 15 May 2020 16:23:42 GMT"
    lm_dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")

    responses.add(
        responses.GET,
        fmt_url,
        body=b'<span data-id="98" data-class="info" data-ident="20200528000000" data-val="1">',
    )
    responses.add(
        responses.POST,
        fmt_url,
        body=bytes(f'<p><a href="/{level}/{filename}">file</a></p>', "utf-8"),
    )
    responses.add(
        responses.HEAD,
        file_url,
        headers={"Content-Length": size, "Last-Modified": last_modified},
    )

    r = xlsx_to_csv.get_files_info(fmt_url)
    assert r[0]["size"] == size
    assert r[0]["last_modified"] == lm_dt
    assert r[0]["url"] == file_url


def test_download_file(mocker):
    """
    Test Parser - Download File
    """
    url = "http://url"
    name = "name"
    path = "path"
    body = b"body"
    responses.add(responses.GET, url, body=body)
    mocker.patch("builtins.open", mocker.mock_open())
    xlsx_to_csv.download_file(url, name, path)
    open().write.assert_any_call(body)
    mocker.resetall()


def test_parse_xlsx(settings):
    """
    Test Parser - Parse xlsx
    """
    filename = "2020-06-13__11__rab_ppe_test.xlsx"
    filepath = os.path.join(settings.APPS_DIR, "rcoi", "tests", "xlsx", filename)
    res = xlsx_to_csv.parse_xlsx(filepath)
    assert len(res) == 10
    assert res[0][0] == filename
    assert res[3][1] == "2020-06-13"
    assert res[5][2] == "11"
    assert "Организатор" in res[8][6]


def test_save_to_csv(mocker_parse_xlsx, csv_headers, csv_data_row, mocker):
    """
    Test Parser - save to csv
    """
    path = "/tmp/data.csv"
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("glob.glob", return_value=["file.xlsx"])
    xlsx_to_csv.save_to_csv(path)
    open().write.assert_any_call(";".join(csv_headers) + "\r\n")
    open().write.assert_any_call(";".join(csv_data_row) + "\r\n")
    mocker.resetall()


def test_save_to_stream(mocker_parse_xlsx, csv_headers, csv_data_row, mocker):
    """
    Test Parser - save to StringIO
    """
    path = "/tmp"
    mocker.patch("glob.glob", return_value=["file.xlsx"])
    res = xlsx_to_csv.save_to_stream(path)
    reader = csv.DictReader(res, delimiter="\t")
    for row in reader:
        for i in range(9):
            assert row[csv_headers[i]] == csv_data_row[i]
    mocker.resetall()


def test_main(mocker_xlsx_to_csv_simple, mocker_os):
    """
    Test Parser - main (stand-alone parser)
    """
    xlsx_to_csv.main()
    assert True
