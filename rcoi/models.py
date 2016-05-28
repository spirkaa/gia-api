from django.db import models
from django_extensions.db import fields as extension_fields
from django_extensions.db.models import TimeStampedModel
from .xls_to_db import get_files, parse_xls, path
import os
import glob
import logging
from time import time

logger = logging.getLogger('rcoi.models')


class ExamDate(TimeStampedModel):
    date = models.DateField('Дата экзамена', unique=True, db_index=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return str(self.date)


class ExamLevel(TimeStampedModel):
    level = models.CharField('Уровень экзамена', max_length=3, unique=True, db_index=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return str(self.level)


class Organisation(TimeStampedModel):
    name = models.CharField('Место работы', max_length=200, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(TimeStampedModel):
    name = models.CharField('Должность в ППЭ', max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(TimeStampedModel):
    name = models.CharField('ФИО', max_length=100, db_index=True)
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'org', 'position'),)
        ordering = ['name']

    def __str__(self):
        return self.name


class Territory(TimeStampedModel):
    code = models.CharField('Код АТЕ', max_length=5, unique=True, db_index=True)
    name = models.CharField('Наименование АТЕ', max_length=100, db_index=True)
    slug = extension_fields.AutoSlugField(populate_from='code', blank=True)

    class Meta:
        verbose_name_plural = 'Territories'
        ordering = ['code']

    def __str__(self):
        return self.name


class Place(TimeStampedModel):
    code = models.CharField('Код ППЭ', max_length=5, db_index=True)
    name = models.CharField('Наименование ППЭ', max_length=200, db_index=True)
    addr = models.CharField('Адрес ППЭ', max_length=150, db_index=True)
    ate = models.ForeignKey(Territory, on_delete=models.CASCADE)
    slug = extension_fields.AutoSlugField(populate_from='code', blank=True)

    class Meta:
        unique_together = (('code', 'name'),)
        ordering = ['code', 'name']

    def __str__(self):
        return self.name


class Exam(TimeStampedModel):
    date = models.ForeignKey(ExamDate, on_delete=models.CASCADE)
    level = models.ForeignKey(ExamLevel, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('date', 'place', 'employee'),)
        # ordering = ['date']

    def __str__(self):
        return str(self.date) + ', ' + str(self.place) + ', ' + str(self.employee)


def db_populate():
    start = time()
    # get_files()
    os.chdir(path)
    for file in glob.glob('*.xlsx')[5:6]:
        data_file = parse_xls(file)
        for line in data_file:
            logger.debug(line)
            date, c = ExamDate.objects.get_or_create(date='2016-{}'.format(line['date'][:5].replace('_', '-')))
            level, c = ExamLevel.objects.get_or_create(level=line['level'])
            ate, c = Territory.objects.get_or_create(code=line['ate_code'],
                                                     defaults={'name': line['ate_name']})
            place, c = Place.objects.get_or_create(code=line['ppe_code'],
                                                   name=line['ppe_name'],
                                                   defaults={'addr': line['ppe_addr'],
                                                             'ate': ate})
            org, c = Organisation.objects.get_or_create(name=line['org'])
            position, c = Position.objects.get_or_create(name=line['position'])
            employee, c = Employee.objects.get_or_create(name=line['name'],
                                                         org=org,
                                                         position=position)
            exam, c = Exam.objects.get_or_create(date=date,
                                                 level=level,
                                                 place=place,
                                                 employee=employee)
            # logger.debug(exam)
        logger.info(round(time() - start, 2))
