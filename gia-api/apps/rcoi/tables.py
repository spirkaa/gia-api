import django_tables2 as tables

from . import models


class EmployeeTable(tables.Table):
    name = tables.TemplateColumn(
        template_name="rcoi/cols/employee_name.html", verbose_name="ФИО"
    )
    org = tables.TemplateColumn(
        template_name="rcoi/cols/employee_org.html", verbose_name="Место работы"
    )

    class Meta:
        model = models.Employee
        sequence = ("name", "org")
        exclude = ("id", "created", "modified")


class PlaceTable(tables.Table):
    name = tables.TemplateColumn(
        template_name="rcoi/cols/place_name.html", verbose_name="Наименование ППЭ"
    )
    addr = tables.TemplateColumn(
        template_name="rcoi/cols/place_addr.html", verbose_name="Адрес ППЭ"
    )

    class Meta:
        model = models.Place
        sequence = ("code", "name", "addr")
        exclude = ("id", "created", "modified", "ate")


class ExamTable(tables.Table):
    date = tables.DateColumn(accessor="date__date")
    level = tables.Column(accessor="level__level")
    code = tables.Column(accessor="place__code")
    place = tables.TemplateColumn(
        template_name="rcoi/cols/exam_place.html", verbose_name="Наименование ППЭ"
    )
    place__addr = tables.TemplateColumn(
        template_name="rcoi/cols/exam_addr.html", verbose_name="Адрес ППЭ"
    )
    position = tables.Column(accessor="position__name")
    employee = tables.TemplateColumn(
        template_name="rcoi/cols/exam_employee.html", verbose_name="ФИО"
    )
    employee__org = tables.TemplateColumn(
        template_name="rcoi/cols/exam_org.html", verbose_name="Место работы"
    )

    class Meta:
        model = models.Exam
        sequence = (
            "date",
            "level",
            "code",
            "place",
            "place__addr",
            "position",
            "employee",
            "employee__org",
        )
        exclude = ("id", "created", "modified", "datafile")
