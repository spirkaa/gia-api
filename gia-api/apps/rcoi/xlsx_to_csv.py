import csv
import glob
import logging
import os
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Comment
from openpyxl import load_workbook

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_file_info(url, date, level):
    """
    Compose info about single exam file from direct url

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
    ext = os.path.splitext(url)[1]
    local_filename = f"{date}__{level}__{ext}"

    file_req = requests.head(url)
    file_req.raise_for_status()
    last_modified = datetime.strptime(
        file_req.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
    )
    file_info = {
        "name": local_filename,
        "url": url,
        "size": file_req.headers["Content-Length"],
        "last_modified": last_modified,
    }
    return file_info


def get_files_info(url):
    """
    Compose custom info about remote files

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

    req = requests.get(url)
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
        block_req = requests.post(url, data=payload, headers=headers)
        block_soup = BeautifulSoup(block_req.text, "lxml")
        # remove comments
        for element in block_soup(text=lambda text: isinstance(text, Comment)):
            element.extract()
        for a in block_soup.select("p a"):
            # skip bad tags
            if not a.attrs:
                continue
            if "rab" in a.attrs.get("href"):
                file_links.append((block[1], urljoin(url, a.attrs.get("href"))))

    result = []
    for block_ident, file_link in file_links:
        # extract date YYYY-MM-DD from block_ident, then combine date, level, filename
        local_filename = "{}-{}-{}__{}__{}".format(
            block_ident[0:4],
            block_ident[4:6],
            block_ident[6:8],
            level,
            os.path.splitext(file_link)[1],
        )
        file_req = requests.head(file_link)
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
    """
    Download file from URL

    :type url: str
    :param url: file url
    :type local_filename: str
    :param local_filename: file name
    :type path: str
    :param path: local path
    """
    logger.debug("download file: %s", local_filename)
    f = os.path.join(path, local_filename)
    if os.path.exists(f):
        raise NotImplementedError(
            "Dumb protection if there are more than 1 file for exam date"
        )
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# quotation marks
re_quotes = re.compile(r'[<>"„“”«»‘’\']')
# spaces before punctuation marks
re_punctuation = re.compile(r"\s+(?=[.,:;!?])")
# (after punctuation marks | before "№" | whitespace chars)
re_spaces = re.compile(r"(?<=[.,:;!№?])(?![.,:;!№?\s])|(?<=\w)(?=№)|\s+")


def apply_regexp(value):
    """
    Apply precompiled regexp rules

    :type value: str
    :param value: string
    :return: formatted string
    :rtype: str
    """
    s = re_spaces.sub(
        " ", re_punctuation.sub("", re_quotes.sub(" ", str(value)))
    ).strip()
    return s


def format_org_name(value):
    """
    Replace full organization name with abbreviation

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
        "Государственное автономное профессиональное общеобразовательное учреждение города Москвы": "ГАПОУ",  # noqa
        "Государственное бюджетное профессиональное общеобразовательное учреждение города Москвы": "ГБПОУ",  # noqa
        "Муниципальное автономное общеобразовательное учреждение": "МАОУ",
    }
    for name, abbreviation in org_names.items():
        value = value.replace(name, abbreviation)
    return value


def format_addr(value):
    """
    Remove district name from street address

    :type value: str
    :param value: original street address
    :return: modified street address
    :rtype: str
    """
    districts = [
        "Восточный",
        "Западный",
        "Зеленоградский",
        "Новомосковский",
        "Северный",
        "Северо-Восточный",
        "Северо-Западный",
        "Троицкий",
        "Центральный",
        "Юго-Восточный",
        "Юго-Западный",
        "Южный",
    ]
    addr = value.split(" ")
    district = addr[1].rstrip(",")
    if district in districts:
        del addr[1]
        return " ".join(addr)
    else:
        return value


def parse_xlsx(filepath):
    """
    Parse Excel file and output result as list of lists (rows)

    :type filepath: str
    :param filepath: local path to excel file
    :return: list of lists
    :rtype: list
    """
    workbook = load_workbook(filepath)
    sheet = workbook[workbook.sheetnames[0]]

    filename = filepath.split("/")[-1]  # linux
    if filename == filepath:  # pragma: no cover
        filename = filepath.split("\\")[-1]  # windows
    filename_parts = filename.split("__")
    exam_date = filename_parts[0]
    exam_level = filename_parts[1]

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
                    if cell_num == 3:  # org address
                        cell = format_addr(cell)
                    if cell_num == 5:  # employee name
                        cell = " ".join([part.capitalize() for part in cell.split()])
                formatted_row.append(cell)  # append all cells, even blank
            if formatted_row[5]:  # why check this?  # pragma: no cover
                result.append(formatted_row)
    return result


def save_to_csv(csv_file):
    """
    Save list of rows to CSV in local file

    :type csv_file: str
    :param csv_file: local CSV file name
    """
    with open(csv_file, "w+", newline="", encoding="utf-8") as fp:
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

    xlsx = os.path.join(os.path.split(csv_file)[0], "*.xlsx")
    for name in glob.glob(xlsx):
        data = parse_xlsx(name)
        if not data:  # pragma: no cover
            continue
        with open(csv_file, "a+", newline="", encoding="utf-8") as fp:
            a = csv.writer(fp, delimiter=";")
            for line in data:
                a.writerow(line)


def save_to_stream(path):
    """
    Save list of rows to CSV in string buffer (memory file)

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

    xlsx = os.path.join(path, "*.xlsx")
    for name in glob.glob(xlsx):
        data = parse_xlsx(name)
        for line in data:
            writer.writerow(line)
    stream.seek(0)
    return stream


def main():
    """
    Download and process files, then output result to local CSV file

    """
    path = "data"
    if not os.path.exists(path):
        os.makedirs(path)
    csv_file = os.path.join(path, path + ".csv")
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
