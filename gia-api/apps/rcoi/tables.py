import django_tables2 as tables

from . import models


class EmployeeTable(tables.Table):
    """Table for employees."""

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


class OrganisationTable(tables.Table):
    """Table for organisations."""

    name = tables.TemplateColumn(
        template_name="rcoi/cols/org_name.html",
        verbose_name="",
        attrs={"td": {"data-title": "Место работы"}},
    )

    class Meta:
        model = models.Organisation
        sequence = ("name",)
        exclude = ("id", "created", "modified", "search_vector")


class PlaceTable(tables.Table):
    """Table for places."""

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
    """Table for exams."""

    date = tables.TemplateColumn(
        template_name="rcoi/cols/date.html",
        verbose_name="Дата",
        attrs={"td": {"data-title": "Дата", "style": "white-space: nowrap"}},
    )
    level = tables.Column(
        accessor="level__level",
        verbose_name="Уровень",
        attrs={"td": {"data-title": "Уровень"}},
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
    """Table for places with exams."""

    date = tables.TemplateColumn(
        template_name="rcoi/cols/date.html",
        verbose_name="Дата",
        attrs={"td": {"data-title": "Дата", "style": "white-space: nowrap"}},
    )
    level = tables.Column(
        accessor="level__level",
        verbose_name="Уровень",
        attrs={"td": {"data-title": "Уровень"}},
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
