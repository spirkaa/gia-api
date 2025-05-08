import csv
from datetime import date, datetime
from pathlib import Path

import pytest
import responses

from apps.rcoi import xlsx_to_csv


def test_prepare_file_info():
    """Test Parser - Prepare File Info."""
    url = "http://rcoi.mcko.ru/"
    filename = "rab_ppe_test.xlsx"
    exam_url = f"{url}/{filename}"
    exam_date = str(date(2020, 6, 1))
    exam_level = "11"
    size = "1024000"
    last_modified = "Fri, 15 May 2020 16:23:42 GMT"
    lm_dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")  # noqa: DTZ007

    responses.add(
        responses.HEAD,
        exam_url,
        headers={"Content-Length": size, "Last-Modified": last_modified},
    )

    r = xlsx_to_csv.prepare_file_info(exam_url, exam_date, exam_level)

    assert r["name"] == f"{exam_date}__{exam_level}__{Path(exam_url).suffix}"
    assert r["size"] == size
    assert r["last_modified"] == lm_dt
    assert r["url"] == exam_url


@pytest.mark.parametrize(
    ("level", "filename"),
    [
        ("wrong", "rab_ppe_test.xlsx"),
        ("oge", "rab_ppe_test.xlsx"),
        ("ege", "Работники_ppe_test.xlsx"),
    ],
)
def test_get_files_info(level, filename):
    """Test Parser - Get Files Info."""
    url = "http://rcoi.mcko.ru/"
    fmt_url = f"{url}{level}/"
    file_url = f"{fmt_url}{filename}"
    size = "1024000"
    last_modified = "Fri, 15 May 2020 16:23:42 GMT"
    lm_dt = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")  # noqa: DTZ007

    responses.add(
        responses.GET,
        fmt_url,
        body=b'<span data-id="98" data-class="info" data-ident="20200528000000" data-val="1">',
    )
    responses.add(
        responses.POST,
        fmt_url,
        body=bytes(
            "<p><a>bad url</a></p>"
            '<p><a href="/index">wrong url</a></p>'
            '<p><!--<a href="#">commented url</a>--></p>'
            f'<p><a href="/{level}/{filename}">file</a></p>',
            "utf-8",
        ),
        content_type="text/plain; charset=utf-8",
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
    """Test Parser - Download File."""
    url = "http://url"
    name = "name"
    path = Path("path")
    body = b"body"
    responses.add(responses.GET, url, body=body)
    opener = mocker.mock_open()
    mocker.patch.object(Path, "open", opener)

    xlsx_to_csv.download_file(url, name, path)

    opener().write.assert_any_call(body)
    mocker.resetall()


@pytest.mark.skip("need to fix")
def test_download_file_if_exists(mocker):
    """Test Parser - Download File if exists."""
    url = "http://url"
    name = "name"
    path = Path("path")
    mocker.patch.object(Path, "exists", return_value=True)

    with pytest.raises(NotImplementedError):
        xlsx_to_csv.download_file(url, name, path)

    mocker.resetall()


def test_load_sheet_data(xlsx_file):
    """Test Parser - Load Sheet Data."""

    res = xlsx_to_csv.load_sheet_data(xlsx_file)
    assert isinstance(res[0][0].value, int)


def test_load_sheet_data_if_file_is_bad(xlsx_file_bad):
    """Test Parser - Load Sheet Data if file is bad."""

    with pytest.raises(xlsx_to_csv.InvalidFileError):
        xlsx_to_csv.load_sheet_data(xlsx_file_bad)


def test_parse_data(xlsx_data, xlsx_file):
    """Test Parser - Parse sheet data."""

    res = xlsx_to_csv.parse_sheet_data(xlsx_data, xlsx_file.name)

    assert len(res) == 10
    assert res[0][0] == xlsx_file.name
    assert res[3][1] == "2020-06-13"
    assert res[5][2] == "11"
    assert "Организатор" in res[8][6]


def test_save_to_csv(mocker_parse_sheet_data, csv_headers, csv_data_row, mocker):
    """Test Parser - save to csv."""
    path = Path("/test/data.csv")
    opener = mocker.mock_open()
    mocker.patch.object(Path, "open", opener)
    mocker.patch("pathlib.Path.glob", return_value=[Path("file.xlsx")])

    xlsx_to_csv.save_to_csv(path)

    opener().write.assert_any_call(";".join(csv_headers) + "\r\n")
    opener().write.assert_any_call(";".join(csv_data_row) + "\r\n")

    mocker.resetall()


def test_save_to_stream(mocker_parse_sheet_data, csv_headers, csv_data_row, mocker):
    """Test Parser - save to StringIO."""
    path = Path("/test")
    mocker.patch("pathlib.Path.glob", return_value=[Path("file.xlsx")])
    res = xlsx_to_csv.save_to_stream(path)
    reader = csv.DictReader(res, delimiter="\t")

    for row in reader:
        for i in range(9):
            assert row[csv_headers[i]] == csv_data_row[i]

    mocker.resetall()


def test_main(mocker_xlsx_to_csv_simple, mocker_path):
    """Test Parser - main (stand-alone parser)."""
    xlsx_to_csv.main()
    assert True  # for coverage
