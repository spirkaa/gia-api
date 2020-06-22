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
    place = tables.TemplateColumn(
        template_name="rcoi/cols/place.html",
        verbose_name="",
        attrs={"td": {"data-title": "ППЭ"}},
    )

    class Meta:
        model = models.Place
        sequence = ("place",)
        exclude = ("id", "created", "modified", "search_vector", "code", "name", "addr")


class ExamTable(tables.Table):
    date = tables.DateColumn(
        accessor="date__date", attrs={"td": {"data-title": "Дата"}}
    )
    level = tables.Column(
        accessor="level__level", attrs={"td": {"data-title": "Уровень"}}
    )
    place = tables.TemplateColumn(
        template_name="rcoi/cols/exam_place.html",
        verbose_name="Код ППЭ, наименование, адрес",
        attrs={"td": {"data-title": "ППЭ"}},
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
            "employee",
            "employee__org",
            "position",
            "place",
        )
        exclude = ("id", "created", "modified", "datafile")


class PlaceWithExamsTable(tables.Table):
    date = tables.DateColumn(
        accessor="date__date", attrs={"td": {"data-title": "Дата"}}
    )
    level = tables.Column(
        accessor="level__level", attrs={"td": {"data-title": "Уровень"}}
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
    position = tables.Column(
        accessor="position__name",
        verbose_name="Должность",
        attrs={"td": {"data-title": "Должность"}},
    )

    class Meta:
        model = models.Exam
        sequence = (
            "date",
            "level",
            "employee",
            "employee__org",
            "position",
        )
        exclude = ("id", "created", "modified", "datafile", "place")
