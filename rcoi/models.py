from django.db import models
from django.core.urlresolvers import reverse
from django_extensions.db.models import TimeStampedModel
import logging
import datetime
import csv
from io import StringIO
from django.db import connection


logger = logging.getLogger('rcoi.models')


class Date(TimeStampedModel):
    date = models.DateField('Дата экзамена', unique=True, db_index=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return str(self.date)

    def get_absolute_url(self):
        return reverse('rcoi:date_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:date_update', args=(self.id,))


class Level(TimeStampedModel):
    level = models.CharField('Уровень экзамена', max_length=3, unique=True, db_index=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return str(self.level)

    def get_absolute_url(self):
        return reverse('rcoi:level_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:level_update', args=(self.id,))


class Organisation(TimeStampedModel):
    name = models.CharField('Место работы', max_length=500, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rcoi:organisation_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:organisation_update', args=(self.id,))


class Position(TimeStampedModel):
    name = models.CharField('Должность в ППЭ', max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rcoi:position_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:position_update', args=(self.id,))


class Employee(TimeStampedModel):
    name = models.CharField('ФИО', max_length=150, db_index=True)
    org = models.ForeignKey(Organisation, related_name='employees', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'org'),)
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rcoi:employee_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:employee_update', args=(self.id,))


class Territory(TimeStampedModel):
    code = models.CharField('Код АТЕ', max_length=5, unique=True, db_index=True)
    name = models.CharField('Наименование АТЕ', max_length=150, db_index=True)

    class Meta:
        verbose_name_plural = 'Territories'
        ordering = ['code']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rcoi:territory_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:territory_update', args=(self.id,))


class Place(TimeStampedModel):
    code = models.CharField('Код ППЭ', max_length=5, db_index=True)
    name = models.CharField('Наименование ППЭ', max_length=500, db_index=True)
    addr = models.CharField('Адрес ППЭ', max_length=255, db_index=True)
    ate = models.ForeignKey(Territory, related_name='places', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('code', 'name', 'addr', 'ate'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rcoi:place_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:place_update', args=(self.id,))


class Exam(TimeStampedModel):
    date = models.ForeignKey(Date, related_name='exams', on_delete=models.CASCADE)
    level = models.ForeignKey(Level, related_name='exams', on_delete=models.CASCADE)
    place = models.ForeignKey(Place, related_name='exams', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, related_name='exams', on_delete=models.CASCADE)
    position = models.ForeignKey(Position, related_name='exams', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('date', 'level', 'place', 'employee'),)
        ordering = ['date']

    def __str__(self):
        return str(self.date) + ', ' + str(self.place) + ', ' + str(self.employee)

    def get_absolute_url(self):
        return reverse('rcoi:exam_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:exam_update', args=(self.id,))


def initial_db_populate():
    import os
    import csv
    from collections import defaultdict
    from time import time
    from .xls_to_db import get_files, save_to_csv

    path = 'data'
    csv_file = 'data.csv'
    os.chdir(path)
    now = time()
    hour_ago = now - 60*60
    if not os.path.isfile(csv_file):
        open(csv_file, 'w+').close()
    file_modified = os.path.getmtime(csv_file)
    if file_modified < hour_ago or os.path.getsize(csv_file) == 0:
        get_files()
        save_to_csv()

    data = defaultdict(list)

    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            for (k, v) in row.items():
                data[k].append(v)

    # Date, Level, Position, Organisation
    for key in ('date', 'level', 'position', 'organisation'):
        values = sorted(list(set(data[key])))
        stream = stream_file(values)
        table = key
        col = 'name'
        if key == 'date' or key == 'level':
            col = key
        columns = (col, 'created', 'modified')
        copy_from(stream, table, *columns)

    # Territory
    ate_code = data['ate_code'][:]
    for i, v in enumerate(ate_code):
        ate_code[i] = int(ate_code[i])
    values = sorted(list(set(zip(ate_code,
                                 data['ate_name']))))
    stream = stream_file(values)
    table = 'territory'
    columns = ('code', 'name', 'created', 'modified')
    copy_from(stream, table, *columns)

    # Employee
    organisation = Organisation.objects.all()
    organisation_db = {org.name: org.id for org in organisation}

    values = sorted(list(set(zip(data['name'],
                                 data['organisation']))))
    values_with_id = [[val[0], organisation_db.get(val[1])] for val in values]
    stream = stream_file(values_with_id)
    table = 'employee'
    columns = ('name', 'org_id', 'created', 'modified')
    copy_from(stream, table, *columns)

    # Place
    territory = Territory.objects.all()
    territory_db = {ate.name: ate.id for ate in territory}
    ppe_code = data['ppe_code'][:]
    for i, v in enumerate(ppe_code):
        ppe_code[i] = int(ppe_code[i])

    values = sorted(list(set(zip(ppe_code,
                                 data['ppe_name'],
                                 data['ppe_addr'],
                                 data['ate_name']))))
    values_with_id = [[*val[:-1], territory_db.get(val[3])] for val in values]
    stream = stream_file(values_with_id)
    table = 'place'
    columns = ('code', 'name', 'addr', 'ate_id', 'created', 'modified')
    copy_from(stream, table, *columns)

    # Exam
    date = Date.objects.all()
    date_db = {str(d.date): d.id for d in date}
    date_id = data['date'][:]
    replace_items(date_id, date_db)

    level = Level.objects.all()
    level_db = {lev.level: lev.id for lev in level}
    level_id = data['level'][:]
    replace_items(level_id, level_db)

    position = Position.objects.all()
    position_db = {pos.name: pos.id for pos in position}
    position_id = data['position'][:]
    replace_items(position_id, position_db)

    place = Place.objects.all()
    place_db = {(p.code, p.name, p.addr): p.id for p in place}
    place_id = list(zip(data['ppe_code'],
                        data['ppe_name'],
                        data['ppe_addr'],))
    replace_items(place_id, place_db)

    employee = Employee.objects.all().select_related()
    employee_db = {(emp.name, emp.org.name): emp.id for emp in employee}
    employee_id = list(zip(data['name'],
                           data['organisation'],))
    replace_items(employee_id, employee_db)

    exams = list(zip(date_id, level_id, place_id, employee_id, position_id))
    stream = stream_file(exams)
    table = 'exam'
    columns = ('date_id', 'level_id', 'place_id',
               'employee_id', 'position_id',
               'created', 'modified')
    copy_from(stream, table, *columns)


def db_update():
    import os
    import csv
    from collections import defaultdict
    from time import time
    from .xls_to_db import get_files, save_to_csv

    path = 'data'
    csv_file = 'data.csv'
    os.chdir(path)
    now = time()
    hour_ago = now - 60*60
    if not os.path.isfile(csv_file):
        open(csv_file, 'w+').close()
    file_modified = os.path.getmtime(csv_file)
    if file_modified < hour_ago or os.path.getsize(csv_file) == 0:
        get_files()
        save_to_csv()

    data = defaultdict(list)

    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            for (k, v) in row.items():
                data[k].append(v)

    # Date, Level, Position, Organisation
    for key in ('date', 'level', 'position', 'organisation'):
        values = sorted(list(set(data[key])))
        # stream = stream_file(values)
        stream = timestamp_list(values)
        table = key
        col = 'name'
        if key == 'date' or key == 'level':
            col = key
        columns = (col, 'created', 'modified')
        sql_insert_or_update(table, columns, stream, col)
        # copy_from(stream, table, *columns)

    # Territory
    ate_code = data['ate_code'][:]
    for i, v in enumerate(ate_code):
        ate_code[i] = int(ate_code[i])
    values = sorted(list(set(zip(ate_code,
                                 data['ate_name']))))
    # stream = stream_file(values)
    stream = timestamp_list(values)
    table = 'territory'
    columns = ('code', 'name', 'created', 'modified')
    sql_insert_or_update(table, columns, stream, columns[0])
    # copy_from(stream, table, *columns)

    # Employee
    organisation = Organisation.objects.all()
    organisation_db = {org.name: org.id for org in organisation}

    values = sorted(list(set(zip(data['name'],
                                 data['organisation']))))
    values_with_id = [[val[0], organisation_db.get(val[1])] for val in values]
    # stream = stream_file(values_with_id)
    stream = timestamp_list(values_with_id)
    table = 'employee'
    columns = ('name', 'org_id', 'created', 'modified')
    sql_insert_or_update(table, columns, stream, columns[:2])
    # copy_from(stream, table, *columns)

    # Place
    territory = Territory.objects.all()
    territory_db = {ate.name: ate.id for ate in territory}
    ppe_code = data['ppe_code'][:]
    for i, v in enumerate(ppe_code):
        ppe_code[i] = int(ppe_code[i])

    values = sorted(list(set(zip(ppe_code,
                                 data['ppe_name'],
                                 data['ppe_addr'],
                                 data['ate_name']))))
    values_with_id = [[*val[:-1], territory_db.get(val[3])] for val in values]
    # stream = stream_file(values_with_id)
    stream = timestamp_list(values_with_id)
    table = 'place'
    columns = ('code', 'name', 'addr', 'ate_id', 'created', 'modified')
    sql_insert_or_update(table, columns, stream, columns[:4])
    # copy_from(stream, table, *columns)

    # Exam
    date = Date.objects.all()
    date_db = {str(d.date): d.id for d in date}
    date_id = data['date'][:]
    replace_items(date_id, date_db)

    level = Level.objects.all()
    level_db = {lev.level: lev.id for lev in level}
    level_id = data['level'][:]
    replace_items(level_id, level_db)

    position = Position.objects.all()
    position_db = {pos.name: pos.id for pos in position}
    position_id = data['position'][:]
    replace_items(position_id, position_db)

    place = Place.objects.all()
    place_db = {(p.code, p.name, p.addr): p.id for p in place}
    place_id = list(zip(data['ppe_code'],
                        data['ppe_name'],
                        data['ppe_addr'],))
    replace_items(place_id, place_db)

    employee = Employee.objects.all().select_related()
    employee_db = {(emp.name, emp.org.name): emp.id for emp in employee}
    employee_id = list(zip(data['name'],
                           data['organisation'],))
    replace_items(employee_id, employee_db)

    exams = list(zip(date_id, level_id, place_id, employee_id, position_id))
    # stream = stream_file(exams)
    stream = timestamp_list(exams)
    table = 'exam'
    columns = ('date_id', 'level_id', 'place_id',
               'employee_id', 'position_id',
               'created', 'modified')
    sql_insert_or_update(table, columns, stream, columns[:4])
    # copy_from(stream, table, *columns)

    # Delete not modified
    for model in (Exam, Employee, Place):
        now = model.objects.latest('modified')
        model.objects.filter(modified__lt=now.modified).delete()


def replace_items(s_list, s_dict):
    for i, item in enumerate(s_list):
        s_list[i] = s_dict.get(item)


def timestamp():
    datetime_now = datetime.datetime.now()
    return [datetime_now, datetime_now]


def timestamp_list(data):
    created = timestamp()
    data_list = []
    for row in data:
        if isinstance(row, (list, tuple, set)):
            row = list(row)
        else:
            row = [row]
        row.extend(created)
        data_list.extend(row)
    return data_list


def stream_file(data):
    created = timestamp()
    stream = StringIO()
    writer = csv.writer(stream, delimiter='\t', quotechar="'")
    for row in data:
        if isinstance(row, (list, tuple, set)):
            row = list(row)
            row.extend(created)
        else:
            row = [row]
            row.extend(created)
        writer.writerow(row)
    stream.seek(0)
    return stream


def sql_insert_or_update(table, columns, data, uniq):
    tablename = 'rcoi_' + table
    colnames = ', '.join(columns).rstrip(', ')
    uniqnames = uniq
    if isinstance(uniq, (list, tuple, set)):
        uniqnames = ', '.join(uniq).rstrip(', ')
    placeholder = ('%s, ' * len(columns)).rstrip(', ')
    rows = ', '.join(['({})'.format(placeholder)] * (len(data) // len(columns)))
    sql = 'INSERT INTO {} ({}) VALUES {} ON CONFLICT ({}) DO UPDATE SET modified=excluded.modified;'.format(
        tablename, colnames, rows, uniqnames)
    with connection.cursor() as cursor:
        cursor.execute(sql, data)


def copy_from(file, table, *columns, sep='\t'):
    with connection.cursor() as cursor:
        cursor.copy_from(
            file=file,
            table='rcoi_' + table,
            sep=sep,
            columns=columns,
        )
