import django_tables2 as tables
from .models import Date, Level, Organisation, Position, Employee, Territory, Place, Exam


class EmployeeTable(tables.Table):
    name = tables.TemplateColumn(template_name='rcoi/cols/employee_name.html',
                                 verbose_name='ФИО')
    org = tables.TemplateColumn(template_name='rcoi/cols/employee_org.html',
                                verbose_name='Место работы')

    class Meta:
        model = Employee
        sequence = ('name', 'org', '...')
        exclude = ('id', 'created', 'modified')


class PlaceTable(tables.Table):
    ate_code = tables.Column(accessor='ate.code')
    ate_name = tables.Column(accessor='ate.name')
    name = tables.TemplateColumn(template_name='rcoi/cols/place_name.html',
                                 verbose_name='Наименование ППЭ')
    addr = tables.TemplateColumn(template_name='rcoi/cols/place_addr.html',
                                 verbose_name='Адрес ППЭ')

    class Meta:
        model = Place
        sequence = ('code', 'name', 'addr', 'ate_code', 'ate_name', '...')
        exclude = ('id', 'created', 'modified', 'ate', 'slug')


class ExamTable(tables.Table):
    date = tables.DateColumn(accessor='date.date')
    level = tables.Column(accessor='level.level')
    code = tables.Column(accessor='place.code')
    place = tables.TemplateColumn(template_name='rcoi/cols/exam_place.html',
                                  verbose_name='Наименование ППЭ')
    addr = tables.TemplateColumn(template_name='rcoi/cols/exam_addr.html',
                                 verbose_name='Адрес ППЭ')
    position = tables.Column(accessor='position.name')
    employee = tables.TemplateColumn(template_name='rcoi/cols/exam_employee.html',
                                     verbose_name='ФИО')
    org = tables.TemplateColumn(template_name='rcoi/cols/exam_org.html',
                                verbose_name='Место работы')

    class Meta:
        model = Exam
        sequence = ('date', 'level', 'code', 'place', 'addr', 'position', 'employee', 'org')
        exclude = ('id', 'created', 'modified')
