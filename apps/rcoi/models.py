import logging
import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import connection, models
from django_extensions.db.models import TimeStampedModel

from apps.rcoi import xlsx_to_csv

logger = logging.getLogger(__name__)

User = get_user_model()


class DataSource(TimeStampedModel):
    name = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка на источник данных')

    class Meta:
        ordering = ['-modified']

    def __str__(self):
        return str(self.name)


class DataFile(TimeStampedModel):
    name = models.CharField('Имя файла', max_length=50)
    url = models.URLField('Ссылка на файл', unique=True)
    size = models.IntegerField('Content-Length', blank=True, null=True)
    last_modified = models.DateTimeField('Last-Modified', blank=True, null=True)

    class Meta:
        ordering = ['-last_modified']

    def __str__(self):
        return str(self.name)


class Date(TimeStampedModel):
    date = models.DateField('Дата экзамена', unique=True, db_index=True)

    class Meta:
        ordering = ['-date']

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
    ate = models.ForeignKey(Territory, related_name='places', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('code', 'name', 'addr'),)
        ordering = ['name']

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
    datafile = models.ForeignKey(DataFile, related_name='exams', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('date', 'level', 'place', 'employee', 'position', 'datafile'),)
        ordering = ['date', 'id']

    def __str__(self):
        return str(self.date) + ', ' + str(self.place) + ', ' + str(self.employee)

    def get_absolute_url(self):
        return reverse('rcoi:exam_detail', args=(self.id,))

    def get_update_url(self):
        return reverse('rcoi:exam_update', args=(self.id,))


class Subscription(TimeStampedModel):
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, related_name='subscriptions', on_delete=models.CASCADE)
    last_send = models.DateTimeField(default=datetime.datetime(2017, 5, 1))

    class Meta:
        unique_together = (('user', 'employee'),)
        ordering = ['employee']

    def __str__(self):
        return str(self.user) + ' --> ' + str(self.employee)


def send_subscriptions():
    from allauth.account.adapter import get_adapter
    from allauth.utils import build_absolute_uri
    from django.core import mail

    template_prefix = 'mail/new_exams'
    location = '/employees/detail/'
    url = build_absolute_uri(None, location, protocol='https')

    subscriptions = Subscription.objects.all().select_related()
    send_queue = {}
    for sub in subscriptions:
        new_exams = []
        context = {
            'exams': new_exams,
            'sub_page': '{}{}'.format(url, sub.employee.id),
            'employee': sub.employee.name
        }
        for exam in sub.employee.exams.all():
            if exam.created > sub.last_send:
                new_exams.append(exam)
        if new_exams:
            send_queue.setdefault(sub.user.email, []).append(context)
            sub.last_send = datetime.datetime.now()
            sub.save()
    if send_queue:
        adapter = get_adapter()
        sender = mail.get_connection()
        messages = []
        for email, context in send_queue.items():
            msg = adapter.send_mail(template_prefix, email, {'context': context})
            messages.append(msg)
        sender.send_messages(messages)


class RcoiUpdater:
    def __init__(self):
        try:
            self.data, self.updated_files = self.__prepare_data()
        except:
            logger.exception('Prepare data for update failed!')
            raise

    def run(self):
        if self.data:
            try:
                self.__update_simple_tables()
                self.__update_employee()
                self.__update_place()
                self.__update_exam()
                self.__update_datafile()
                self.__cleanup()
                return True
            except:
                logger.exception('Update failed!')
                raise

    def __prepare_data(self):
        import csv
        import os
        import shutil
        from collections import defaultdict

        urls = DataSource.objects.all()
        try:
            urls.latest('modified')
        except DataSource.DoesNotExist:
            raise
        tmp_path = 'tmp'

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        files_info = [xlsx_to_csv.get_files_info(url.url) for url in urls]
        files_info = [url for url_list in files_info for url in url_list]

        updated_files = []
        for file in files_info:
            url = file['url']
            name = file['name']
            try:
                f = DataFile.objects.get(url=url)
                if f.last_modified != file['last_modified']:
                    updated_files.append(file)
                    logger.debug('%s: dates differ, DOWNLOAD', name)
                else:
                    logger.debug('%s: dates are the same, SKIP', name)
            except DataFile.DoesNotExist:
                logger.debug('%s: file not found, DOWNLOAD', name)
                DataFile.objects.create(**file)
                updated_files.append(file)

        if updated_files:
            data = defaultdict(list)

            [xlsx_to_csv.download_file(file['url'], file['name'], tmp_path) for file in updated_files]
            csv_stream = xlsx_to_csv.save_to_stream(tmp_path)

            reader = csv.DictReader(csv_stream, delimiter='\t')
            for row in reader:
                for (k, v) in row.items():
                    data[k].append(v)
            logger.debug('cleanup downloaded files')
            shutil.rmtree(tmp_path)
            return data, updated_files
        return None, None

    def __cleanup(self):
        from django.core.cache import cache
        cache.clear()

        logger.debug('cleanup unneeded exam rows from updated files')
        files = DataFile.objects.all()
        files_modified = files.filter(modified__gte=datetime.datetime.now() - datetime.timedelta(minutes=5))
        exams = Exam.objects.all()
        to_delete = []
        for file in files_modified:
            modified = file.modified - datetime.timedelta(minutes=5)
            filtered = exams.filter(modified__lt=modified, datafile_id=file.id)
            if filtered.count() > 0:
                to_delete.append(filtered)
        for qs in to_delete:
            count = qs.delete()
            logger.debug('rows deleted: %s', count[0])
        cache.clear()

    def __sql_insert_or_update(self, table, columns, data, uniq):
        from django.core.cache import cache
        cache.clear()

        table_name = 'rcoi_' + table
        col_names = ', '.join(columns).rstrip(', ')
        uniq_names = uniq
        if isinstance(uniq, (list, tuple, set)):
            uniq_names = ', '.join(uniq).rstrip(', ')
        placeholder = ('%s, ' * len(columns)).rstrip(', ')
        rows = ', '.join(['({})'.format(placeholder)] * (len(data) // len(columns)))
        sql = 'INSERT INTO {} ({}) VALUES {} ON CONFLICT ({}) DO UPDATE SET modified=excluded.modified;'.format(
            table_name, col_names, rows, uniq_names)
        with connection.cursor() as cursor:
            cursor.execute(sql, data)

    def __update_datafile(self):
        for file in self.updated_files:
            logger.debug('update or create file: %s', file['name'])
            DataFile.objects.update_or_create(url=file['url'], defaults=file)

    def __update_simple_tables(self):
        for key in ('date', 'level', 'position', 'organisation'):
            values = sorted(list(set(self.data[key])))
            stream = timestamp_list(values)
            table = key
            col = 'name'
            if key == 'date' or key == 'level':
                col = key
            columns = (col, 'created', 'modified')
            logger.debug('processing model: %s', table)
            self.__sql_insert_or_update(table, columns, stream, col)

    def __update_employee(self):
        organisation = Organisation.objects.all()
        organisation_db = {org.name: org.id for org in organisation}

        values = sorted(list(set(zip(self.data['name'],
                                     self.data['organisation']))))
        values_with_id = [[val[0], organisation_db.get(val[1])] for val in values]
        stream = timestamp_list(values_with_id)
        table = 'employee'
        columns = ('name', 'org_id', 'created', 'modified')
        logger.debug('processing model: %s', table)
        self.__sql_insert_or_update(table, columns, stream, columns[:2])

    def __update_place(self):
        ppe_code = self.data['ppe_code'][:]
        for i, v in enumerate(ppe_code):
            ppe_code[i] = int(ppe_code[i])

        values = sorted(list(set(zip(ppe_code,
                                     self.data['ppe_name'],
                                     self.data['ppe_addr']))))
        stream = timestamp_list(values)
        table = 'place'
        columns = ('code', 'name', 'addr', 'created', 'modified')
        logger.debug('processing model: %s', table)
        self.__sql_insert_or_update(table, columns, stream, columns[:3])

    def __update_exam(self):
        date = Date.objects.all()
        date_db = {str(d.date): d.id for d in date}
        date_id = self.data['date'][:]
        replace_items(date_id, date_db)

        level = Level.objects.all()
        level_db = {lev.level: lev.id for lev in level}
        level_id = self.data['level'][:]
        replace_items(level_id, level_db)

        position = Position.objects.all()
        position_db = {pos.name: pos.id for pos in position}
        position_id = self.data['position'][:]
        replace_items(position_id, position_db)

        place = Place.objects.all()
        place_db = {(p.code, p.name, p.addr): p.id for p in place}
        place_id = list(zip(self.data['ppe_code'],
                            self.data['ppe_name'],
                            self.data['ppe_addr'], ))
        replace_items(place_id, place_db)

        employee = Employee.objects.all().select_related()
        employee_db = {(emp.name, emp.org.name): emp.id for emp in employee}
        employee_id = list(zip(self.data['name'],
                               self.data['organisation'], ))
        replace_items(employee_id, employee_db)

        datafile = DataFile.objects.all()
        datafile_db = {df.name: df.id for df in datafile}
        datafile_id = self.data['datafile'][:]
        replace_items(datafile_id, datafile_db)

        exams = list(zip(date_id, level_id, place_id, employee_id, position_id, datafile_id))

        table = 'exam'
        columns = ('date_id', 'level_id', 'place_id',
                   'employee_id', 'position_id', 'datafile_id',
                   'created', 'modified')
        logger.debug('processing model: %s', table)

        for chunk in split_list(exams, 20):
            stream = timestamp_list(chunk)
            self.__sql_insert_or_update(table, columns, stream, columns[:6])


def replace_items(s_list, s_dict):
    for i, item in enumerate(s_list):
        s_list[i] = s_dict.get(item)


def timestamp_list(data):
    datetime_now = datetime.datetime.now()
    created = [datetime_now, datetime_now]
    data_list = []
    for row in data:
        if isinstance(row, (list, tuple, set)):
            row = list(row)
        else:
            row = [row]
        row.extend(created)
        data_list.extend(row)
    return data_list


def split_list(seq, chunks):
    avg = (len(seq) // chunks) + 1
    out = []
    last = 0
    while last < len(seq):
        out.append(seq[last:last + avg])
        last += avg
    return out


def cursor_execute(sql):
    # sql = 'DROP TABLE rcoi_subscription;'
    # sql = 'DELETE FROM rcoi_exam;'
    with connection.cursor() as cursor:
        cursor.execute(sql)
