import csv
import logging
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Comment
from openpyxl import load_workbook

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_file_info(url, date, level):
    """Compose info about single exam file from direct url.

    :type url: str
    :param url: file url
    :type date: str
    :param date: exam date
    :type level: str
    :param level: exam level
    :return: files headers
    :rtype: dict
    """
    logger.debug("get file info: %s", url)
    ext = Path(url).suffix
    local_filename = f"{date}__{level}__{ext}"

    file_req = requests.head(url, timeout=5)
    file_req.raise_for_status()
    last_modified = datetime.strptime(
        file_req.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
    )
    return {
        "name": local_filename,
        "url": url,
        "size": file_req.headers["Content-Length"],
        "last_modified": last_modified,
    }


def get_files_info(url):
    """Compose custom info about remote files.

    :type url: str
    :param url: file url
    :return: files headers
    :rtype: list
    """
    logger.debug("get file links: %s", url)
    if "/ege/" in url:
        level = "11"
    elif "/oge/" in url:
        level = "9"
    else:
        level = "0"

    req = requests.get(url, timeout=5)
    soup = BeautifulSoup(req.text, "lxml").select('span[data-class="info"]')
    content_blocks = [
        (block.attrs.get("data-id"), block.attrs.get("data-ident")) for block in soup
    ]

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }

    file_links = []
    for block in content_blocks:
        payload = "id={}&data={}&val=1".format(*block)
        block_req = requests.post(url, data=payload, headers=headers, timeout=5)
        block_soup = BeautifulSoup(block_req.text, "lxml")
        # remove comments
        for element in block_soup(string=lambda string: isinstance(string, Comment)):
            element.extract()
        for a in block_soup.select("p a"):
            # skip bad tags
            if not a.attrs:
                continue
            href = a.attrs.get("href", "")
            if not href:
                continue
            if "rab" in href.lower() or "работники" in href.lower():
                file_links.append((block[1], urljoin(url, href)))

    result = []
    for block_ident, file_link in file_links:
        # extract date YYYY-MM-DD from block_ident, then combine date, level, filename
        local_filename = f"{block_ident[0:4]}-{block_ident[4:6]}-{block_ident[6:8]}__{level}__{Path(file_link).suffix}"
        file_req = requests.head(file_link, timeout=5)
        if file_req:
            last_modified = datetime.strptime(
                file_req.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
            )
            file_info = {
                "name": local_filename,
                "url": file_link,
                "size": file_req.headers["Content-Length"],
                "last_modified": last_modified,
            }
            result.append(file_info)
    return result


def download_file(url, local_filename, path):
    """Download file from URL.

    :type url: str
    :param url: file url
    :type local_filename: str
    :param local_filename: file name
    :type path: str
    :param path: local path
    """
    logger.debug("download file: %s", local_filename)
    f = Path(path).joinpath(local_filename)
    if f.exists():
        logger.error("There are more than 1 file for exam date: %s", local_filename)
        return
    with requests.get(url, stream=True, timeout=5) as r:
        r.raise_for_status()
        with Path(f).open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# quotation marks
re_quotes = re.compile(r'[<>"„“”«»‘’\']')
# spaces before punctuation marks
re_punctuation = re.compile(r"\s+(?=[.,:;!?])")
# (after punctuation marks | before "№" | whitespace chars)
re_spaces = re.compile(r"(?<=[.,:;!№?])(?![.,:;!№?\s])|(?<=\w)(?=№)|\s+")


def apply_regexp(value):
    """Apply precompiled regexp rules.

    :type value: str
    :param value: string
    :return: formatted string
    :rtype: str
    """
    return re_spaces.sub(
        " ", re_punctuation.sub("", re_quotes.sub(" ", str(value)))
    ).strip()


def format_org_name(value):
    """Replace full organization name with abbreviation.

    :type value: str
    :param value: original name
    :return: modified name
    :rtype: str
    """
    org_names = {
        "Государствнное": "Государственное",
        "уччреждение": "учреждение",
        "бюджетного": "бюджетное",
        " образовательное": " общеобразовательное",
        "им.": "имени",
        "Государственное бюджетное общеобразовательное учреждение города Москвы": "ГБОУ",
        "Государственное бюджетное общеобразовательное учреждение": "ГБОУ",
        "Государственное казенное общеобразовательное учреждение города Москвы": "ГКОУ",
        "Государственное автономное общеобразовательное учреждение города Москвы": "ГАОУ",
        "Государственное автономное профессиональное общеобразовательное учреждение города Москвы": "ГАПОУ",
        "Государственное бюджетное профессиональное общеобразовательное учреждение города Москвы": "ГБПОУ",
        "Муниципальное автономное общеобразовательное учреждение": "МАОУ",
    }
    for name, abbreviation in org_names.items():
        value = value.replace(name, abbreviation)
    return value


def parse_xlsx(file_path):
    """Parse Excel file and output result as list of lists (rows).

    :type file_path: str
    :param file_path: local path to excel file
    :return: list of lists
    :rtype: list
    """
    workbook = load_workbook(file_path)
    sheet = workbook[workbook.sheetnames[0]]

    filename = file_path.name
    exam_date, exam_level, *_ = filename.split("__")

    if len(tuple(sheet.columns)) < 7:  # pragma: no cover
        logger.debug("skip file %s: wrong number of columns", filename)
        return []

    sheet_data = tuple(sheet.rows)
    sheet_rows_count = len(sheet_data)

    logger.debug(
        "parse file: %s (date %s, level %s, rows %s)",
        filename,
        exam_date,
        exam_level,
        sheet_rows_count - 2,
    )

    result = []
    for row_index in range(2, sheet_rows_count):  # skip 2 rows (headers)
        row = sheet_data[row_index]
        formatted_row = [filename, exam_date, exam_level]
        if isinstance(row[0].value, int):  # process only rows where 1 cell = int
            for cell_num in range(1, len(row)):  # skip 1 cell (int counter)
                cell = row[cell_num].value
                if cell:
                    cell = apply_regexp(cell)
                    if cell_num == 2 or cell_num == 6:  # org name
                        cell = format_org_name(cell)
                    if cell_num == 5:  # employee name
                        cell = " ".join([part.capitalize() for part in cell.split()])
                formatted_row.append(cell)  # append all cells, even blank
            if formatted_row[5]:  # why check this?  # pragma: no cover
                result.append(formatted_row)
    return result


def save_to_csv(csv_file):
    """Save list of rows to CSV in local file.

    :type csv_file: str
    :param csv_file: local CSV file name
    """
    with Path(csv_file).open("w+", newline="", encoding="utf-8") as fp:
        a = csv.writer(fp, delimiter=";")
        a.writerow(
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

    parent_dir = Path(csv_file).parent
    for file_name in parent_dir.glob("*.xlsx"):
        data = parse_xlsx(file_name)
        if not data:  # pragma: no cover
            continue
        with Path(csv_file).open("a+", newline="", encoding="utf-8") as fp:
            a = csv.writer(fp, delimiter=";")
            for line in data:
                a.writerow(line)


def save_to_stream(path):
    """Save list of rows to CSV in string buffer (memory file).

    :type path: str
    :param path: local directory with xlsx files
    :return: memory file
    """
    from io import StringIO

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

    for name in Path(path).glob("*.xlsx"):
        data = parse_xlsx(name)
        for line in data:
            writer.writerow(line)
    stream.seek(0)
    return stream


def main():
    """Download and process files, then output result to local CSV file."""
    path = "data"
    if not Path(path).exists():
        Path(path).mkdir(parents=True)
    csv_file = Path(path).joinpath(f"{path}.csv")
    urls = [
        "http://rcoi.mcko.ru/organizers/schedule/oge/?period=1",
        "http://rcoi.mcko.ru/organizers/schedule/ege/?period=1",
        "http://rcoi.mcko.ru/organizers/schedule/oge/?period=2",
        "http://rcoi.mcko.ru/organizers/schedule/ege/?period=2",
        "http://rcoi.mcko.ru/organizers/schedule/oge/?period=3",
        "http://rcoi.mcko.ru/organizers/schedule/ege/?period=3",
    ]
    files_info = [get_files_info(url) for url in urls]
    files_info = [url for url_list in files_info for url in url_list]
    [download_file(file["url"], file["name"], path) for file in files_info]
    save_to_csv(csv_file)


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(
        format="%(asctime)s  [%(name)s:%(lineno)s]  %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    main()
