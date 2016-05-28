import os
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook
import csv
import glob
import logging

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
    if not os.path.exists(path):
        os.makedirs(path)

    local_filename = url.split('/')[-1]
    fs = requests.get(url, stream=True)
    with open(os.path.join(path, local_filename), 'wb') as f:
        for chunk in fs.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_files():
    files = [get_links(url) for url in pages]
    for i in range(len(files)):
        [download_file(url) for url in files[i] if 'rab' in url]


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
    logger.info('%s, %s класс: %s rows', file, level, rowcount)
    l_data = []
    for rowno in range(2, rowcount):
        row = data[rowno]
        l_row = [file, level]
        for cellno in range(len(row)):
            l_row.append(row[cellno].value)
        names = ['date', 'level', 'ate_code', 'ate_name',
                 'ppe_code', 'ppe_name', 'ppe_addr',
                 'position', 'name', 'org']
        if l_row[2]:
            # l_data.append(dict(zip(names, l_row)))
            l_data.append(l_row)
    return l_data


def save_to_csv():
    os.chdir(path)
    with open('data.csv', 'w+', newline='') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerow(['file', 'level',
                    'код АТЕ', 'наименование АТЕ',
                    'Код ППЭ', 'Наименование ППЭ',
                    'Адрес ППЭ', 'Должность в ППЭ',
                    'Ф. И. О.', 'Наименование организации места работы'])

    for file in glob.glob('*.xlsx'):
        data = parse_xls(file)
        with open('data.csv', 'a+', newline='') as fp:
            a = csv.writer(fp, delimiter=';')
            for line in data:
                a.writerow(line)


def main():
    # get_files()
    save_to_csv()

if __name__ == '__main__':
    main()
