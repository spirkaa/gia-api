import sys

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.requests import RequestSite
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DetailView, ListView, TemplateView
from django_tables2 import RequestConfig

from .filters import EmployeeFilter, ExamFilter, PlaceFilter, PlaceWithExamsFilter
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
from .tables import EmployeeTable, ExamTable, PlaceTable, PlaceWithExamsTable


class TemplateViewWithContext(TemplateView):
    model = None
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sources"] = DataSource.objects.all()
        try:
            context["updated"] = DataFile.objects.latest("modified").modified
        except DataFile.DoesNotExist:
            context["updated"] = ""
        context["link_rel"] = "{}://{}{}".format(
            self.request.scheme, RequestSite(self.request).domain, self.request.path
        )
        return context


class HomeView(TemplateViewWithContext):
    template_name = "rcoi/home.html"


class FilteredSingleTableView(TemplateViewWithContext):
    table_class = None
    paginate_by = 50
    filter_class = None

    def get_queryset(self, **kwargs):
        return self.model.objects.select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = self.filter_class(
            self.request.GET, queryset=self.get_queryset(**kwargs)
        )
        filter.form.helper = self.filter_class().helper
        table = self.table_class(filter.qs)
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(
            table
        )
        context["filter"] = filter
        context["table"] = table
        try:
            context["table_sort"] = self.request.GET["sort"]
        except MultiValueDictKeyError:
            pass
        return context


class EmployeeTableView(FilteredSingleTableView):
    model = Employee
    table_class = EmployeeTable
    filter_class = EmployeeFilter
    template_name = "rcoi/employee.html"


class PlaceTableView(FilteredSingleTableView):
    model = Place
    table_class = PlaceTable
    filter_class = PlaceFilter
    template_name = "rcoi/place.html"


class ExamTableView(FilteredSingleTableView):
    model = Exam
    table_class = ExamTable
    filter_class = ExamFilter
    template_name = "rcoi/exam.html"


class DetailViewWithContext(DetailView):
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sources"] = DataSource.objects.all()
        try:
            context["updated"] = DataFile.objects.latest("modified").modified
        except DataFile.DoesNotExist:
            context["updated"] = ""
        context["link_rel"] = "{}://{}{}".format(
            self.request.scheme, RequestSite(self.request).domain, self.request.path
        )
        return context


class OrganisationDetailView(DetailViewWithContext):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employees"] = self.object.employees.annotate(
            num_exams=Count("exams")
        ).order_by("name")
        return context


class EmployeeDetailView(DetailViewWithContext):
    model = Employee

    def get_queryset(self):
        return super().get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exams"] = self.object.exams.select_related()
        return context


class PlaceDetailView(FilteredSingleTableView):
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


class DateListView(ListView):
    model = Date


class DateDetailView(DetailView):
    model = Date


class LevelListView(ListView):
    model = Level


class LevelDetailView(DetailView):
    model = Level


class OrganisationListView(ListView):
    model = Organisation


class PositionListView(ListView):
    model = Position


class PositionDetailView(DetailView):
    model = Position


class ExamDetailView(DetailView):
    model = Exam


@staff_member_required
def update_db_view(request):
    if request.method == "POST":
        # noinspection PyBroadException
        try:
            updated = RcoiUpdater().run()
            if updated:
                messages.info(request, "База данных обновлена!")
            else:
                messages.info(request, "Изменений нет!")
        except:  # noqa  # pragma: no cover
            messages.error(request, sys.exc_info())
    return redirect(reverse("admin:index"))


@staff_member_required
def clear_caches_view(request):
    if request.method == "POST":
        # noinspection PyBroadException
        try:
            from django.core.cache import cache

            res = cache.clear()
            messages.info(request, "Кэш очищен! Удалено ключей: {}".format(res))
        except:  # noqa  # pragma: no cover
            messages.error(request, sys.exc_info())
    return redirect(reverse("admin:index"))
