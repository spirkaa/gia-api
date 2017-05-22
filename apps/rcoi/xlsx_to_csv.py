import os
import csv
import glob
import logging
import re
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s [%(name)s:%(lineno)s] %(levelname)s - %(message)s',
    level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)


def get_links(url):
    logger.debug('get file links: %s', url)
    url_base = '/'.join(url.split('/')[:3])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.select('.article-content a')
    return [url_base + a.attrs.get('href') for a in content]


def download_file(url, path):
    logger.debug('download file: %s', url)
    local_filename = url.split('/')[-1]
    fs = requests.get(url, stream=True)
    with open(os.path.join(path, local_filename), 'wb') as f:
        for chunk in fs.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_files(url, path):
    file_links = get_links(url)
    [download_file(file_link, path) for file_link in file_links if 'rab' in file_link]


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
    if len(tuple(ws.columns)) < 9:
        logger.debug('skip file %s: wrong number of columns', filename)
        return None
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
    logger.debug('parse file: %s (date %s, level %s, records %s)', filename, date, level, row_count-2)
    l_data = []
    for row_num in range(2, row_count):
        row = data[row_num]
        l_row = [date, level]
        for cell_num in range(len(row)):
            cell = row[cell_num].value
            if cell:
                cell = re_work(cell)
                if ' образовательное учреждение' in cell:
                    cell = cell.replace(' образовательное учреждение', ' общеобразовательное учреждение')
                if 'учреждение школа' in cell:
                    cell = cell.replace('учреждение школа', 'учреждение города Москвы Школа')
                if 'ГБОУ' in cell:
                    cell = cell.replace('ГБОУ', 'Государственное бюджетное общеобразовательное учреждение города Москвы')
            l_row.append(cell)
        if l_row[2]:
            l_data.append(l_row)
    return l_data


def save_to_csv(csv_file):
    with open(csv_file, 'w+', newline='', encoding='utf-8') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerow(['date', 'level', 'ate_code', 'ate_name',
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
    import sys
    stream = StringIO()
    writer = csv.writer(stream, delimiter='\t', quotechar="'")
    writer.writerow(['date', 'level', 'ate_code', 'ate_name',
                     'ppe_code', 'ppe_name', 'ppe_addr',
                     'position', 'name', 'organisation'])

    xlsx = os.path.join(path, '*.xlsx')
    for name in glob.glob(xlsx):
        data = parse_xlsx(name)
        logger.info(sys.getsizeof(data))
        for line in data:
            writer.writerow(line)
    stream.seek(0)
    return stream


def main():
    path = 'data'
    if not os.path.exists(path):
        os.makedirs(path)
    csv_file = os.path.join(path, path + '.csv')
    pages = ['http://rcoi.mcko.ru/index.php?option=com_content&view=article&id=896&Itemid=196',
             'http://rcoi.mcko.ru/index.php?option=com_content&view=article&id=958&Itemid=203']
    [get_files(url, path) for url in pages]
    save_to_csv(csv_file)

if __name__ == '__main__':
    main()
