import functools
import operator

import django_filters
from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db.models import F, Q

from . import models


class SearchVectorFilter(django_filters.CharFilter):
    """
    django-filter filter_overrides for django.contrib.postgres.search.SearchVectorField
    """

    def __init__(
        self, field_name=None, lookup_expr="icontains", *, search_fields, **kwargs
    ):
        super().__init__(field_name, lookup_expr, **kwargs)
        self.search_fields = search_fields

    def filter(self, qs, value):
        if value in django_filters.filters.EMPTY_VALUES:
            return qs

        query = SearchQuery(
            " | ".join(value.split()), search_type="raw", config="russian"
        )

        # sum of ranks of all vector fields
        sum_of_ranks = sum(
            [SearchRank(F(field), query) for field in self.search_fields]
        )

        # Generate F encapsulated filters and combine them using logical OR
        # Input:  [{"search_vector": query}, {"org__search_vector": query}]
        # Output: Q(search_vector=query) | Q(org__search_vector=query)
        filters = [{field: query} for field in self.search_fields]
        combined_filters = functools.reduce(operator.or_, [Q(**kw) for kw in filters])
        qs = (
            qs.annotate(rank=sum_of_ranks)
            .filter(rank__gt=0.0)
            .filter(combined_filters)
            .order_by("-rank")
        )
        return qs


class FilterWithHelper(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_show_labels = False
        self.helper.form_id = "filter"
        self.helper.layout = Layout(
            FieldWithButtons(
                Field("search", placeholder="Поиск..."), Submit("", "Найти")
            ),
        )
        self._meta.filter_overrides = {
            SearchVectorField: {"filter_class": SearchVectorFilter,}
        }


class EmployeeFilter(FilterWithHelper):
    search = SearchVectorFilter(
        search_fields=["search_vector", "org__search_vector"], label="Поиск"
    )

    class Meta:
        model = models.Employee
        fields = ["search"]


class PlaceFilter(FilterWithHelper):
    search = SearchVectorFilter(search_fields=["search_vector"], label="Поиск")

    class Meta:
        model = models.Place
        fields = ["search"]


class ExamFilter(FilterWithHelper):
    search = SearchVectorFilter(
        search_fields=[
            "employee__search_vector",
            "employee__org__search_vector",
            "position__search_vector",
            "place__search_vector",
        ],
        label="Поиск",
    )

    class Meta:
        model = models.Exam
        fields = ["search"]
