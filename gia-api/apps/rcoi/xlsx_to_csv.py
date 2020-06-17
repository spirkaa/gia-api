import csv
import glob
import logging
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


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
        level = 11
    elif "/oge/" in url:
        level = 9
    else:
        level = "other"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml").select('span[data-class="info"]')
    content_blocks = [
        (block.attrs.get("data-id"), block.attrs.get("data-ident")) for block in soup
    ]

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    url_base = "/".join(url.split("/")[:3])  # == http://domain.com

    file_links = []
    for block in content_blocks:
        payload = "id={}&data={}&val=1".format(*block)
        block_req = requests.request("POST", url, data=payload, headers=headers)
        block_soup = BeautifulSoup(block_req.text, "lxml").select("p a")
        file_links += [
            (block[1], url_base + a.attrs.get("href"))
            for a in block_soup
            if "rab" in a.attrs.get("href")
        ]

    result = []
    for block_ident, file_link in file_links:
        # extract date YYYY-MM-DD from block_ident, then combine date, level, filename
        local_filename = "{}-{}-{}__{}__{}".format(
            block_ident[0:4],
            block_ident[4:6],
            block_ident[6:8],
            level,
            file_link.split("/")[-1],
        )
        file_req = requests.head(file_link)
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
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(path, local_filename), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# replace quotation marks
s0 = re.compile(r'["„“”«»\'‘’]')
# remove spaces before punctuation marks
s1 = re.compile(r"\s+(?=[.,:;!?])")
# 1. (add space after punctuation marks |
# 2. add space before "№" |
# 3. replace whitespace chars with only one space)
s2 = re.compile(r"(?<=[.,:;!№?])(?![.,:;!№?\s])|(?<=\w)(?=№)|\s+")


def re_work(s):
    """
    Format string with precompiled regexp rules

    :type s: str
    :param s: string
    :return: formatted string
    :rtype: str
    """
    s = s2.sub(" ", s1.sub("", s0.sub(" ", str(s)))).strip()
    return s


def rename_org(value):  # pragma: no cover
    """
    Replace parts of organization name

    :type value: str
    :param value: original name
    :return: modified name
    :rtype: str
    """
    if " образовательное учреждение" in value:
        value = value.replace(
            " образовательное учреждение", " общеобразовательное учреждение",
        )
    value = value.replace(
        "Федеральное государственное бюджетное общеобразовательное учреждение высшего образования",
        "ФГБОУ ВО",
    )
    value = value.replace(
        "федеральное государственное бюджетное общеобразовательное учреждение высшего образования",
        "ФГБОУ ВО",
    )
    value = value.replace(
        "Федеральное государственное бюджетное общеобразовательное учреждение", "ФГБОУ"
    )
    value = value.replace(
        "Автономная некоммерческая образовательная организация", "АНОО"
    )
    value = value.replace(
        "Автономная некомерческая организация высшего образования", "АНОВО"
    )
    value = value.replace(
        "Автономная некоммерческая общеобразовательная организация", "АНОО"
    )
    value = value.replace(
        "Государственное автономное общеобразовательное учреждение города Москвы",
        "ГАОУ",
    )
    value = value.replace(
        "Государственное автономное общеобразовательное учреждение дополнительного профессионального образования города Москвы",  # noqa
        "ГАОУ ДПО",
    )
    value = value.replace(
        "Государственное автономное общеобразовательное учреждение высшего образования города Москвы",
        "ГАОУ ВО",
    )
    value = value.replace(
        "Государственное автономное профессиональное общеобразовательное учреждение города Москвы",
        "ГАПОУ",
    )
    value = value.replace(
        "Государственное бюджетное профессиональное общеобразовательное учреждение города Москвы",
        "ГБПОУ",
    )
    value = value.replace(
        "Государственное бюджетное профессиональное общеобразовательное учреждение (колледж) города Москвы",  # noqa
        "ГБПОУ",
    )
    value = value.replace(
        "Государственное бюджетное профессиональное общеобразовательное учреждение г. Москвы",
        "ГБПОУ",
    )
    value = value.replace("ГБПОУ г. Москвы", "ГБПОУ")
    value = value.replace(
        "Государственное бюджетное общеобразовательное учреждение города Москвы", "ГБОУ"
    )
    value = value.replace(
        "Государственное бюджетное общеобразовательноеучреждение города Москвы", "ГБОУ"
    )
    value = value.replace(
        "Государственное бюджетное общеобразовательное учреждение", "ГБОУ"
    )
    value = value.replace(
        "государственное бюджетное общеобразовательное учреждение", "ГБОУ"
    )
    value = value.replace("Государственное бюджетное учреждение города Москвы", "ГБУ")
    value = value.replace(
        "Государственное бюджетное учреждение средняя общеобразовательная школа",
        "ГБУ СОШ",
    )
    value = value.replace(
        "Государственное казенное общеобразовательное учреждение города Москвы", "ГКОУ"
    )
    value = value.replace(
        "Муниципальное автономное общеобразовательное учреждение", "МАОУ"
    )
    value = value.replace(
        "Негосударственная общеобразовательная организация частное учреждение", "НООЧУ"
    )
    value = value.replace(
        "Негосударственное образовательное частное учреждение", "НОЧУ"
    )
    value = value.replace(
        "Негосударственное образовательное частное учреждения", "НОЧУ"
    )
    value = value.replace(
        "Негосударственное некоммерческое общеобразовательное учреждение", "ННОУ"
    )
    value = value.replace("Негосударственное общеобразовательное учреждение", "НОУ")
    value = value.replace(
        "Негосударственное общеобразовательное частное учреждение", "НОЧУ"
    )
    value = value.replace(
        "Негосударственное частное учреждение общеобразовательная организация", "НЧУОО"
    )
    value = value.replace("Некоммерческое образовательное частное учреждение", "НОЧУ")
    value = value.replace(
        "Общеобразовательная автономная некоммерческая организация", "ОАНО"
    )
    value = value.replace("Автономная некоммерческая организация", "АНО")
    value = value.replace("Общеобразовательное частное учреждение", "ОЧУ")
    value = value.replace("Образовательное частное учреждение", "ОЧУ")
    value = value.replace("Общеобразовательная организация частное учреждение", "ООЧУ")
    value = value.replace(
        "Общеобщеобразовательная автономная некоммерческая организация", "ОАНО"
    )
    value = value.replace("средняя общеобразовательная школа", "СОШ")
    value = value.replace("Средняя общеобразовательная школа", "СОШ")
    value = value.replace(
        "Федеральное государственное автономное общеобразовательное учреждение", "ФГАОУ"
    )
    value = value.replace(
        "федеральное государственное бюджетное общеобразовательное учреждение", "ФГБОУ"
    )
    value = value.replace(
        "Федеральное государственное бюджетное общеобразовательное учреждение", "ФГБОУ"
    )
    value = value.replace(
        "Федеральное государственное казенное общеобразовательное учреждение", "ФГКОУ"
    )
    value = value.replace(
        "Федеральное государственное казённое общеобразовательное учреждение", "ФГКОУ"
    )
    value = value.replace("Частное общеобразовательное учреждение", "ЧОУ")
    value = value.replace("Частное учреждение общеобразовательная организация", "ЧУ ОО")
    value = value.replace("Частное учреждение Общеобразовательная организация", "ЧУ ОО")
    value = value.replace(
        "Частное учреждение средняя общеобразовательная школа", "ЧУ СОШ"
    )
    value = value.replace(
        "Частное учреждение средняя общеобразовательное школа", "ЧУ СОШ"
    )
    value = value.replace(
        "Частное учреждение Средняя общеобразовательная школа", "ЧУ СОШ"
    )
    value = value.replace("Частное учреждение", "ЧУ")
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
                    cell = re_work(cell)
                    cell = rename_org(cell)
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
