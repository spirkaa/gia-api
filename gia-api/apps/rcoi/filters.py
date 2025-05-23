import functools
import operator
import re

import django_filters
from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db.models import F, Q

from . import models


def dates_filtered_by_exams_in_place(request):
    """Dates filtered by exams in place.

    :type request: object
    :param request: django request object
    :return: queryset
    :rtype: object
    """
    if request is None:
        return models.Date.objects.all()
    return models.Date.objects.filter(
        exams__place=request.resolver_match.kwargs["pk"],
    ).distinct()


class SearchVectorFilter(django_filters.CharFilter):
    """django-filter filter_overrides for django.contrib.postgres.search.SearchVectorField."""

    def __init__(
        self,
        field_name=None,
        lookup_expr="icontains",
        *,
        search_fields,
        **kwargs,
    ):
        super().__init__(field_name, lookup_expr, **kwargs)
        self.search_fields = search_fields

    def filter(self, qs, value):
        """Full text search.

        :type qs: object
        :type value: str
        """
        if value in django_filters.filters.EMPTY_VALUES:
            return qs

        query = SearchQuery(
            " | ".join(re.sub(r"[\\()&!|<>:\']", " ", value).split()),
            search_type="raw",
            config="russian",
        )

        # sum of ranks of all vector fields
        sum_of_ranks = sum(SearchRank(F(field), query) for field in self.search_fields)

        # Generate F encapsulated filters and combine them using logical OR
        # Input:  [{"search_vector": query}, {"org__search_vector": query}]  # noqa: ERA001
        # Output: Q(search_vector=query) | Q(org__search_vector=query)  # noqa: ERA001
        filters = [{field: query} for field in self.search_fields]
        combined_filters = functools.reduce(operator.or_, [Q(**kw) for kw in filters])
        return (
            qs.annotate(rank=sum_of_ranks)
            .filter(rank__gt=0.0)
            .filter(combined_filters)
            .order_by("-rank")
        )


class FilterWithHelper(django_filters.FilterSet):
    """FilterSet with crispy_forms layout."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_show_labels = False
        self.helper.form_id = "filter"
        self.helper.layout = Layout(
            FieldWithButtons(
                Field(
                    "search",
                    placeholder="Поиск...",
                    aria_Label="Поиск",
                    autocomplete="off",
                    autofocus="",
                    css_class="form-control",
                ),
                HTML(
                    """
                    {% if request.GET.search %}
                    <a href="{{ request.path }}"
                        role="button"
                        class="btn btn-default"
                        title="Очистить">
                        ✕
                    </a>
                    {% endif %}
                    """,
                ),
                Submit("", "Найти"),
            ),
        )
        self._meta.filter_overrides = {
            SearchVectorField: {
                "filter_class": SearchVectorFilter,
            },
        }


class EmployeeFilter(FilterWithHelper):
    """Filter for employees."""

    search = SearchVectorFilter(
        search_fields=["search_vector", "org__search_vector"],
        label="Поиск",
    )

    class Meta:
        model = models.Employee
        fields = ["search"]


class OrganisationFilter(FilterWithHelper):
    """Filter for organisations."""

    search = SearchVectorFilter(search_fields=["search_vector"], label="Поиск")

    class Meta:
        model = models.Organisation
        fields = ["search"]


class PlaceFilter(FilterWithHelper):
    """Filter for places."""

    search = SearchVectorFilter(search_fields=["search_vector"], label="Поиск")

    class Meta:
        model = models.Place
        fields = ["search"]


class ExamFilter(FilterWithHelper):
    """Filter for exams."""

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


class PlaceWithExamsFilter(FilterWithHelper):
    """Filter for places with exams."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_class = "form-inline form-group text-center"
        self.helper.layout = Layout(
            "date",
            Field(
                "search",
                placeholder="Поиск...",
                aria_Label="Поиск",
                autocomplete="off",
                autofocus="",
            ),
            HTML(
                """
                {% if request.GET.search or request.GET.date %}
                <a href="{{ request.path }}"
                    role="button"
                    class="btn btn-default"
                    title="Очистить">
                    ✕
                </a>
                {% endif %}
                """,
            ),
            Submit("", "Найти"),
        )

    date = django_filters.ModelChoiceFilter(
        queryset=dates_filtered_by_exams_in_place,
        empty_label="Все даты",
    )
    search = SearchVectorFilter(
        search_fields=[
            "employee__search_vector",
            "employee__org__search_vector",
            "position__search_vector",
        ],
        label="Поиск",
    )

    class Meta:
        model = models.Exam
        fields = ["date", "search"]
