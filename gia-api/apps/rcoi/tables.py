import django_tables2 as tables

from . import models


class EmployeeTable(tables.Table):
    name = tables.TemplateColumn(
        template_name="rcoi/cols/employee_name.html",
        verbose_name="ФИО",
        attrs={"td": {"data-title": "ФИО"}},
    )
    org = tables.TemplateColumn(
        template_name="rcoi/cols/employee_org.html",
        verbose_name="Место работы",
        attrs={"td": {"data-title": "Место работы"}},
    )

    class Meta:
        model = models.Employee
        sequence = ("name", "org")
        exclude = ("id", "created", "modified", "search_vector")


class PlaceTable(tables.Table):
    code = tables.Column(attrs={"td": {"data-title": "Код ППЭ"}})
    name = tables.TemplateColumn(
        template_name="rcoi/cols/place_name.html",
        verbose_name="Наименование ППЭ",
        attrs={"td": {"data-title": "Наименование ППЭ"}},
    )
    addr = tables.TemplateColumn(
        template_name="rcoi/cols/place_addr.html",
        verbose_name="Адрес ППЭ",
        attrs={"td": {"data-title": "Адрес ППЭ"}},
    )

    class Meta:
        model = models.Place
        sequence = ("code", "name", "addr")
        exclude = ("id", "created", "modified", "search_vector")


class ExamTable(tables.Table):
    date = tables.DateColumn(
        accessor="date__date", attrs={"td": {"data-title": "Дата"}}
    )
    level = tables.Column(
        accessor="level__level", attrs={"td": {"data-title": "Уровень"}}
    )
    code = tables.Column(
        accessor="place__code", attrs={"td": {"data-title": "Код ППЭ"}}
    )
    place = tables.TemplateColumn(
        template_name="rcoi/cols/exam_place.html",
        verbose_name="Наименование ППЭ",
        attrs={"td": {"data-title": "Наим. ППЭ"}},
    )
    place__addr = tables.TemplateColumn(
        template_name="rcoi/cols/exam_addr.html",
        verbose_name="Адрес ППЭ",
        attrs={"td": {"data-title": "Адрес ППЭ"}},
    )
    position = tables.Column(
        accessor="position__name",
        verbose_name="Должность",
        attrs={"td": {"data-title": "Должность"}},
    )
    employee = tables.TemplateColumn(
        template_name="rcoi/cols/exam_employee.html",
        verbose_name="ФИО",
        attrs={"td": {"data-title": "ФИО"}},
    )
    employee__org = tables.TemplateColumn(
        template_name="rcoi/cols/exam_org.html",
        verbose_name="Место работы",
        attrs={"td": {"data-title": "Место работы"}},
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
