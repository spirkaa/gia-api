import django_tables2 as tables
from .models import Date, Level, Organisation, Position, Employee, Territory, Place, Exam


class EmployeeTable(tables.Table):
    name = tables.TemplateColumn(
        '<a href="{{record.get_absolute_url}}">{{record.name}}</a>',
        verbose_name='ФИО')
    org = tables.TemplateColumn(
        '<a href="{{record.org.get_absolute_url}}">{{record.org.name}}</a>',
        verbose_name='Место работы')

    class Meta:
        model = Employee
        sequence = ('name', 'org', '...')
        exclude = ('id', 'created', 'modified')


class PlaceTable(tables.Table):
    ate_code = tables.Column(accessor='ate.code')
    ate_name = tables.Column(accessor='ate.name')
    addr = tables.TemplateColumn(
        '<a href="https://yandex.ru/maps/?text={{record.addr}}" target="_blank" title="Открыть карту">{{record.addr}}</a>',
        verbose_name='Адрес ППЭ')

    class Meta:
        model = Place
        sequence = ('code', 'name', 'addr', 'ate_code', 'ate_name', '...')
        exclude = ('id', 'created', 'modified', 'ate', 'slug')


class ExamTable(tables.Table):
    date = tables.DateColumn(accessor='date.date')
    level = tables.Column(accessor='level.level')
    code = tables.Column(accessor='place.code')
    place = tables.Column(accessor='place.name')
    addr = tables.TemplateColumn(
        '<a href="https://yandex.ru/maps/?text={{record.place.addr}}" target="_blank" title="Открыть карту">{{record.place.addr}}</a>',
        verbose_name='Адрес ППЭ')
    position = tables.Column(accessor='position.name')
    employee = tables.TemplateColumn(
        '<a href="{{record.employee.get_absolute_url}}">{{record.employee.name}}</a>',
        verbose_name='ФИО')
    org = tables.Column(accessor='employee.org.name')

    class Meta:
        model = Exam
        sequence = ('date', 'level', 'code', 'place', 'addr', 'position', 'employee', 'org')
        exclude = ('id', 'created', 'modified')
