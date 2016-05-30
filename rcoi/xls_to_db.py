import os
import csv
import glob
import logging
import re
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

logger = logging.getLogger('xlsx_to_csv')
logging.basicConfig(
    format='%(asctime)s [%(name)s:%(lineno)s] %(levelname)s - %(message)s',
    level=logging.DEBUG)

path = 'data'
pages = ['/index.php?option=com_content&view=article&id=1033&Itemid=211',
         '/index.php?option=com_content&view=article&id=898&Itemid=197']


def get_links(url):
    url_base = 'http://rcoi.mcko.ru'
    r = requests.get(url_base + url)
    soup = BeautifulSoup(r.text, 'lxml')
    content = soup.select('.article-content a')
    return [url_base + a.attrs.get('href') for a in content]


def download_file(url):
    # if not os.path.exists(path):
    #     os.makedirs(path)

    local_filename = url.split('/')[-1]
    fs = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in fs.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_files():
    files = [get_links(url) for url in pages]
    for i in range(len(files)):
        [download_file(url) for url in files[i] if 'rab' in url]


def re_work(s):
    # replace quotation marks
    s0 = re.compile('["„“”«»\'‘’]')
    # remove spaces before punctuation marks
    s1 = re.compile('\s+(?=[\.,:;!\?])')
    # 1. (add space after punctuation marks |
    # 2. add space before "№" |
    # 3. replace whitespace chars with only one space)
    s2 = re.compile('(?<=[\.,:;!№\?])(?![\.,:;!№\?\s])|(?<=\w)(?=№)|\s+')
    s = s2.sub(' ', s1.sub('', s0.sub(' ', str(s)))).strip()
    return s


def parse_xls(file):
    wb = load_workbook(file)
    ws = wb[wb.get_sheet_names()[0]]
    data = ws.rows
    rowcount = len(data)
    level = 9
    if 'единого' in data[0][0].value:
        level = 11
    elif 'выпускного' in data[0][0].value:
        level = 'ГВЭ'
    logger.info('%s, %s: %s rows', file, level, rowcount-2)
    date = '2016-{}'.format(file[:5].replace('_', '-'))
    l_data = []
    for rowno in range(2, rowcount):
        row = data[rowno]
        l_row = [date, level]
        for cellno in range(len(row)):
            cell = row[cellno].value
            if cell:
                cell = re_work(cell)
                if 'д. 1 А. корп. 8' in cell:
                    cell = cell.replace('д. 1 А. корп. 8', 'д. 1А, корпус 8')
                if 'д. 1 А' in cell:
                    cell = cell.replace('1 А', '1а')
                if 'д. 165 Е' in cell:
                    cell = cell.replace('165 Е', '165Е')
                if 'д. 10 А' in cell:
                    cell = cell.replace('10 А', '10А')
                if 'д. 8а' in cell:
                    cell = cell.replace('д. 8а', 'д. 8А')
                if '127521' in cell:
                    cell = cell.replace('127521', '127018')
                if '109387' in cell:
                    cell = cell.replace('109387', '109559')
                if '124681' in cell:
                    cell = cell.replace('124681', '124527')
                if 'Васильцовский стан' in cell:
                    cell = cell.replace('стан', 'Стан')
                if 'Капотни' in cell:
                    cell = cell.replace('Капотни', 'Капотня')
                if 'г. г.' in cell:
                    cell = cell.replace('г. г.', 'г.')
                if 'ул. Зеленоград' in cell:
                    cell = cell.replace('ул. Зеленоград', 'г. Зеленоград')
                if 'город Зеленоград' in cell:
                    cell = cell.replace('город Зеленоград', 'г. Зеленоград')
                if 'лицей' in cell:
                    cell = cell.replace('лицей', 'Лицей')
                if 'средняя общеобразовательная школа № 2044' in cell:
                    cell = cell.replace('средняя общеобразовательная школа № 2044', 'Школа № 2044')
                if ' образовательное учреждение' in cell:
                    cell = cell.replace(' образовательное учреждение', ' общеобразовательное учреждение')
                if 'учреждение школа' in cell:
                    cell = cell.replace('учреждение школа', 'учреждение города Москвы Школа')
                if 'Департамента социальной' in cell:
                    cell = cell.replace('Департамента социальной', 'Департамента труда и социальной')
                if 'ГБОУ' in cell:
                    cell = cell.replace('ГБОУ', 'Государственное бюджетное общеобразовательное учреждение города Москвы')
            l_row.append(cell)
        names = ['date', 'level', 'ate_code', 'ate_name',
                 'ppe_code', 'ppe_name', 'ppe_addr',
                 'position', 'name', 'org']
        if l_row[2]:
            # l_data.append(dict(zip(names, l_row)))
            l_data.append(l_row)
    return l_data


def save_to_csv():
    # os.chdir(path)
    with open('data.csv', 'w+', newline='', encoding='utf-8') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerow(['date', 'level', 'ate_code', 'ate_name',
                    'ppe_code', 'ppe_name', 'ppe_addr',
                    'position', 'name', 'organisation'])

    for file in glob.glob('*.xlsx'):
        data = parse_xls(file)
        with open('data.csv', 'a+', newline='', encoding='utf-8') as fp:
            a = csv.writer(fp, delimiter=';')
            for line in data:
                a.writerow(line)


def main():
    pass
    get_files()
    save_to_csv()

if __name__ == '__main__':
    main()
