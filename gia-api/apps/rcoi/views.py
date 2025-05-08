import contextlib
import sys

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.requests import RequestSite
from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DetailView, ListView, TemplateView
from django_tables2 import RequestConfig

from .filters import (
    EmployeeFilter,
    ExamFilter,
    OrganisationFilter,
    PlaceFilter,
    PlaceWithExamsFilter,
)
from .models import (
    DataFile,
    DataSource,
    Date,
    Employee,
    Exam,
    Level,
    Organisation,
    Place,
    Position,
    RcoiUpdater,
)
from .tables import (
    EmployeeTable,
    ExamTable,
    OrganisationTable,
    PlaceTable,
    PlaceWithExamsTable,
)


class TemplateViewWithContext(TemplateView):
    """Base template view that provides additional context data for templates."""

    model = None
    template_name = None

    def get_context_data(self, **kwargs):
        """Get the context data for the template, including data sources, last update, and link relation."""
        context = super().get_context_data(**kwargs)
        context["sources"] = DataSource.objects.all()
        try:
            context["updated"] = DataFile.objects.latest("modified").modified
        except DataFile.DoesNotExist:
            context["updated"] = ""
        context["link_rel"] = (
            f"{self.request.scheme}://{RequestSite(self.request).domain}{self.request.path}"
        )
        return context


class HomeView(TemplateViewWithContext):
    """Home page view."""

    template_name = "rcoi/home.html"


class FilteredSingleTableView(TemplateViewWithContext):
    """Base view for table with filtered data."""

    table_class = None
    paginate_by = 50
    filter_class = None

    def get_queryset(self, **kwargs):
        return self.model.objects.select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_ = self.filter_class(
            data=self.request.GET,
            request=self.request,
            queryset=self.get_queryset(**kwargs),
        )
        filter_.form.helper = self.filter_class().helper
        table = self.table_class(filter_.qs)
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(
            table,
        )
        context["filter"] = filter_
        context["table"] = table
        with contextlib.suppress(MultiValueDictKeyError):
            context["table_sort"] = self.request.GET["sort"]

        return context


class EmployeeTableView(FilteredSingleTableView):
    """Table view for employees."""

    model = Employee
    table_class = EmployeeTable
    filter_class = EmployeeFilter
    template_name = "rcoi/employee.html"


class OrganisationTableView(FilteredSingleTableView):
    """Table view for organisations."""

    model = Organisation
    table_class = OrganisationTable
    filter_class = OrganisationFilter
    template_name = "rcoi/organisation.html"


class PlaceTableView(FilteredSingleTableView):
    """Table view for places."""

    model = Place
    table_class = PlaceTable
    filter_class = PlaceFilter
    template_name = "rcoi/place.html"


class ExamTableView(FilteredSingleTableView):
    """Table view for exams."""

    model = Exam
    table_class = ExamTable
    filter_class = ExamFilter
    template_name = "rcoi/exam.html"


class DetailViewWithContext(DetailView):
    """Base detail view that provides additional context data for templates."""

    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sources"] = DataSource.objects.all()
        try:
            context["updated"] = DataFile.objects.latest("modified").modified
        except DataFile.DoesNotExist:
            context["updated"] = ""
        context["link_rel"] = (
            f"{self.request.scheme}://{RequestSite(self.request).domain}{self.request.path}"
        )
        return context


class OrganisationDetailView(DetailViewWithContext):
    """Detail view for organisation."""

    model = Organisation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employees"] = (
            self.object.employees.annotate(num_exams=Count("exams"))
            .prefetch_related(
                "exams__date",
                "exams__level",
                "exams__place",
                "exams__position",
            )
            .order_by("name")
        )
        context["dates"] = (
            Date.objects.filter(
                id__in=[
                    exam.date_id
                    for employee in context["employees"]
                    for exam in employee.exams.all()
                ],
            )
            .distinct()
            .order_by("-date")
        )
        return context


class EmployeeDetailView(DetailViewWithContext):
    """Detail view for employee."""

    model = Employee

    def get_queryset(self):
        return super().get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exams"] = self.object.exams.select_related()
        return context


class PlaceDetailView(FilteredSingleTableView):
    """Detail view for place."""

    model = Exam
    table_class = PlaceWithExamsTable
    filter_class = PlaceWithExamsFilter
    template_name = "rcoi/place_detail.html"

    def get_queryset(self, **kwargs):
        return self.model.objects.filter(place=self.kwargs.get("pk")).select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["place"] = Place.objects.filter(pk=self.kwargs.get("pk")).get()
        return context

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Place.DoesNotExist:
            raise Http404 from None


class DateListView(ListView):
    """List view for dates."""

    model = Date


class DateDetailView(DetailView):
    """Detail view for a date."""

    model = Date


class LevelListView(ListView):
    """List view for levels."""

    model = Level


class LevelDetailView(DetailView):
    """Detail view for a level."""

    model = Level


class PositionListView(ListView):
    """List view for positions."""

    model = Position


class PositionDetailView(DetailView):
    """Detail view for a position."""

    model = Position


class ExamDetailView(DetailView):
    """Detail view for an exam."""

    model = Exam


@staff_member_required
def update_db_view(request):
    """Update database."""
    if request.method == "POST":
        # noinspection PyBroadException
        try:
            updated = RcoiUpdater().run()
            if updated:
                messages.info(request, "База данных обновлена!")
            else:
                messages.info(request, "Изменений нет!")
        except Exception:  # noqa: BLE001
            messages.error(request, sys.exc_info())
    return redirect(reverse("admin:index"))


@staff_member_required
def clear_caches_view(request):
    """Clear all caches."""
    if request.method == "POST":
        # noinspection PyBroadException
        try:
            from django.core.cache import cache

            res = cache.clear()
            messages.info(request, f"Кэш очищен! Удалено ключей: {res}")
        except Exception:  # noqa: BLE001
            messages.error(request, sys.exc_info())
    return redirect(reverse("admin:index"))
