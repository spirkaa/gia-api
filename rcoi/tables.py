import django_tables2 as tables
from .models import ExamDate, ExamLevel, Organisation, Position, Employee, Territory, Place, Exam


class EmployeeTable(tables.Table):
    org = tables.Column(accessor='org.name')
    position = tables.Column(accessor='position.name')

    class Meta:
        model = Employee
        sequence = ('name', 'org', 'position', '...')
        exclude = ('id', 'created', 'modified')


class PlaceTable(tables.Table):
    ate_code = tables.Column(accessor='ate.code')
    ate_name = tables.Column(accessor='ate.name')

    class Meta:
        model = Place
        sequence = ('code', 'name', 'addr', 'ate_code', 'ate_name', '...')
        exclude = ('id', 'created', 'modified', 'ate', 'slug')


class ExamTable(tables.Table):
    date = tables.DateColumn(accessor='date.date')
    level = tables.Column(accessor='level.level')
    code = tables.Column(accessor='place.code')
    place = tables.Column(accessor='place.name')
    addr = tables.Column(accessor='place.addr')
    pos = tables.Column(accessor='employee.position.name')
    employee = tables.Column(accessor='employee.name')
    org = tables.Column(accessor='employee.org.name')

    class Meta:
        model = Exam
        sequence = ('date', 'level', 'code', 'place', 'addr', 'pos', 'employee', 'org', '...')
        exclude = ('id', 'created', 'modified')
