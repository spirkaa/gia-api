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
logging.basicConfig(
    format='%(asctime)s [%(name)s:%(lineno)s] %(levelname)s - %(message)s',
    level=logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_files_info(url):
    logger.debug('get file links: %s', url)
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'cache-control': 'no-cache'
    }
    fmt_dt = '%a, %d %b %Y %H:%M:%S %Z'
    url_base = '/'.join(url.split('/')[:3])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.select('span[data-class="info"]')
    blocks = [(block.attrs.get('data-id'), block.attrs.get('data-ident')) for block in content]

    links = []
    for block in blocks:
        payload = 'id={}&data={}&val=1'.format(*block)
        r2 = requests.request('POST', url, data=payload, headers=headers)
        soup2 = BeautifulSoup(r2.text, 'lxml')
        content2 = soup2.select('p a')
        links += [url_base + a.attrs.get('href') for a in content2 if 'rab' in a.attrs.get('href')]

    files_info = []
    for link in links:
        local_filename = link.split('/')[-1]
        r3 = requests.head(link)
        lmd = datetime.strptime(r3.headers['Last-Modified'], fmt_dt)
        file = {
            'name': local_filename,
            'url': link,
            'size': r3.headers['Content-Length'],
            'last_modified': lmd
        }
        files_info.append(file)
    return files_info


def download_file(url, path):
    local_filename = url.split('/')[-1]
    logger.debug('download file: %s', local_filename)
    fs = requests.get(url, stream=True)
    with open(os.path.join(path, local_filename), 'wb') as f:
        for chunk in fs.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


# replace quotation marks
s0 = re.compile('["„“”«»\'‘’]')
# remove spaces before punctuation marks
s1 = re.compile('\s+(?=[.,:;!?])')
# 1. (add space after punctuation marks |
# 2. add space before "№" |
# 3. replace whitespace chars with only one space)
s2 = re.compile('(?<=[.,:;!№?])(?![.,:;!№?\s])|(?<=\w)(?=№)|\s+')


def re_work(s):
    s = s2.sub(' ', s1.sub('', s0.sub(' ', str(s)))).strip()
    return s


def extract_date(header):
    months = {
        'января': '01', 'февраля': '02', 'марта': '03',
        'апреля': '04', 'мая': '05', 'июня': '06',
        'июля': '07', 'августа': '08', 'сентярбя': '09',
        'октября': '10', 'ноября': '11', 'декарбя': '12'
    }
    date = header[-4:-1]
    date[1] = months[date[1]]
    if int(date[0]) < 10:
        date[0] = '0' + date[0]
    return '-'.join(reversed(date))


def parse_xlsx(filename):
    wb = load_workbook(filename)
    ws = wb[wb.get_sheet_names()[0]]
    if len(tuple(ws.columns)) < 8:
        logger.debug('skip file %s: wrong number of columns', filename)
        return []
    data = tuple(ws.rows)
    row_count = len(data)
    header = data[0][0].value.split()
    if 'единого' in header:
        level = 11
    elif 'выпускного' in header:
        level = 'ГВЭ'
    else:
        level = 9
    date = extract_date(header)
    filename = filename.split('/')[-1]
    logger.debug('parse file: %s (date %s, level %s, rows %s)', filename, date, level, row_count-2)
    l_data = []
    prev_value_of_cell_0 = 0
    prev_value_of_cell_1 = 0
    for row_num in range(2, row_count):
        row = data[row_num]
        l_row = [filename, date, level]
        for cell_num in range(len(row)):
            cell = row[cell_num].value
            # Тупое хачество из-за косяка в файле РЦОИ
            # там в 2 строках отсутствуют 2 ячейки
            if cell and cell_num == 0:
                prev_value_of_cell_0 = cell
            if cell and cell_num == 1:
                prev_value_of_cell_1 = cell
            if not cell and cell_num == 0:
                cell = prev_value_of_cell_0
            if not cell and cell_num == 1:
                cell = prev_value_of_cell_1
            if cell:
                cell = re_work(cell)
                if ' образовательное учреждение' in cell:
                    cell = cell.replace(' образовательное учреждение', ' общеобразовательное учреждение')
                if 'учреждение школа' in cell:
                    cell = cell.replace('учреждение школа', 'учреждение города Москвы Школа')
                if 'ГБОУ' in cell:
                    cell = cell.replace('ГБОУ', 'Государственное бюджетное общеобразовательное учреждение города Москвы')
            l_row.append(cell)
        if l_row[5]:
            l_data.append(l_row)
    return l_data


def save_to_csv(csv_file):
    with open(csv_file, 'w+', newline='', encoding='utf-8') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerow(['datafile', 'date', 'level',
                    'ate_code', 'ate_name',
                    'ppe_code', 'ppe_name', 'ppe_addr',
                    'position', 'name', 'organisation'])

    xlsx = os.path.join(os.path.split(csv_file)[0], '*.xlsx')
    for name in glob.glob(xlsx):
        data = parse_xlsx(name)
        if not data:
            continue
        with open(csv_file, 'a+', newline='', encoding='utf-8') as fp:
            a = csv.writer(fp, delimiter=';')
            for line in data:
                a.writerow(line)


def save_to_stream(path):
    from io import StringIO
    stream = StringIO()
    writer = csv.writer(stream, delimiter='\t', quotechar="'")
    writer.writerow(['datafile', 'date', 'level',
                     'ate_code', 'ate_name',
                     'ppe_code', 'ppe_name', 'ppe_addr',
                     'position', 'name', 'organisation'])

    xlsx = os.path.join(path, '*.xlsx')
    for name in glob.glob(xlsx):
        data = parse_xlsx(name)
        for line in data:
            writer.writerow(line)
    stream.seek(0)
    return stream


def main():
    path = 'data'
    if not os.path.exists(path):
        os.makedirs(path)
    csv_file = os.path.join(path, path + '.csv')
    urls = ['http://rcoi.mcko.ru/organizers/schedule/oge/?period=2',
             'http://rcoi.mcko.ru/organizers/schedule/ege/?period=2']
    files_info = [get_files_info(url) for url in urls]
    files_info = [url for url_list in files_info for url in url_list]
    [download_file(file['url'], path) for file in files_info]
    save_to_csv(csv_file)

if __name__ == '__main__':
    main()
