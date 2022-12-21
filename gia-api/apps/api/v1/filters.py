import rest_framework_filters as filters

from apps.rcoi import models
from apps.rcoi.filters import SearchVectorFilter


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class DateFilter(filters.FilterSet):
    date = filters.CharFilter(lookup_expr="icontains", label="Дата экзамена")

    class Meta:
        model = models.Date
        fields = ("date",)


class LevelFilter(filters.FilterSet):
    level = filters.CharFilter(lookup_expr="icontains", label="Уровень")

    class Meta:
        model = models.Level
        fields = ("level",)


class OrganisationFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="Место работы")
    search = SearchVectorFilter(
        search_fields=["search_vector"], label="Поиск", help_text="Full Text Search"
    )

    class Meta:
        model = models.Organisation
        fields = ("name", "search")


class PositionFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="Должность в ППЭ")
    search = SearchVectorFilter(
        search_fields=["search_vector"], label="Поиск", help_text="Full Text Search"
    )

    class Meta:
        model = models.Position
        fields = ("name", "search")


class EmployeeFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")

    name = filters.CharFilter(lookup_expr="icontains", label="ФИО сотрудника")
    org_id = filters.CharFilter(field_name="org__id", label="id места работы")
    org_name = filters.CharFilter(
        field_name="org__name", lookup_expr="icontains", label="Место работы"
    )
    search = SearchVectorFilter(
        search_fields=["search_vector", "org__search_vector"],
        label="Поиск",
        help_text="Full Text Search",
    )

    class Meta:
        model = models.Employee
        fields = ("id", "name", "org_id", "org_name", "search")


class PlaceFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")

    name = filters.CharFilter(lookup_expr="icontains", label="Наименование ППЭ")
    addr = filters.CharFilter(lookup_expr="icontains", label="Адрес ППЭ")
    search = SearchVectorFilter(
        search_fields=["search_vector"], label="Поиск", help_text="Full Text Search"
    )

    class Meta:
        model = models.Place
        fields = ("id", "code", "name", "addr", "search")


class ExamFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")

    date = filters.DateFilter(
        field_name="date__date", lookup_expr="icontains", label="Дата экзамена"
    )
    level = filters.CharFilter(
        field_name="level__level", lookup_expr="icontains", label="Уровень"
    )
    pos = filters.CharFilter(
        field_name="position__name", lookup_expr="icontains", label="Должность в ППЭ"
    )
    p_id = filters.CharFilter(field_name="place__id", label="id ППЭ")
    p_code = filters.CharFilter(field_name="place__code", label="Код ППЭ")
    p_name = filters.CharFilter(
        field_name="place__name", lookup_expr="icontains", label="Наименование ППЭ"
    )
    p_addr = filters.CharFilter(
        field_name="place__addr", lookup_expr="icontains", label="Адрес ППЭ"
    )
    emp_id = filters.CharFilter(field_name="employee__id", label="id сотрудника")
    emp_name = filters.CharFilter(
        field_name="employee__name", lookup_expr="icontains", label="ФИО сотрудника"
    )
    emp_org_id = filters.CharFilter(
        field_name="employee__org__id", label="id места работы"
    )
    emp_org_name = filters.CharFilter(
        field_name="employee__org__name", lookup_expr="icontains", label="Место работы"
    )
    search = SearchVectorFilter(
        search_fields=[
            "employee__search_vector",
            "employee__org__search_vector",
            "position__search_vector",
            "place__search_vector",
        ],
        label="Поиск",
        help_text="Full Text Search",
    )

    class Meta:
        model = models.Exam
        fields = (
            "id",
            "date",
            "level",
            "pos",
            "p_id",
            "p_code",
            "p_name",
            "p_addr",
            "emp_id",
            "emp_name",
            "emp_org_id",
            "emp_org_name",
            "search",
        )
