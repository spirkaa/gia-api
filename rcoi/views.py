from django.db.models import Count, Max
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView, ListView, View
from django_tables2 import RequestConfig

from .filters import EmployeeFilter, PlaceFilter, ExamFilter
from .models import Date, Level, Organisation, Position, Employee, Territory, Place, Exam
from .models import initial_db_populate, db_update
from .tables import EmployeeTable, PlaceTable, ExamTable


class FilteredSingleTableView(TemplateView):
    model = None
    table_class = None
    paginate_by = 50
    filter_class = None
    template_name = None

    def get_queryset(self, **kwargs):
        return self.model.objects.select_related()

    def get_context_data(self, **kwargs):
        context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
        filter = self.filter_class(self.request.GET,
                                   queryset=self.get_queryset(**kwargs))
        filter.form.helper = self.filter_class().helper
        table = self.table_class(filter.qs)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(table)
        context['filter'] = filter
        context['table'] = table
        context['updated'] = Exam.objects.aggregate(upd_date=Max('modified'))['upd_date']
        return context


class EmployeeTableView(FilteredSingleTableView):
    model = Employee
    table_class = EmployeeTable
    filter_class = EmployeeFilter
    template_name = 'rcoi/employee.html'


class PlaceTableView(FilteredSingleTableView):
    model = Place
    table_class = PlaceTable
    filter_class = PlaceFilter
    template_name = 'rcoi/place.html'


class ExamTableView(FilteredSingleTableView):
    model = Exam
    table_class = ExamTable
    filter_class = ExamFilter
    template_name = 'rcoi/exam.html'


class OrganisationDetailView(DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailView, self).get_context_data(**kwargs)
        context['employees'] = self.object.employees.annotate(num_exams=Count('exams'))
        context['updated'] = Exam.objects.aggregate(upd_date=Max('modified'))['upd_date']
        return context


class EmployeeDetailView(DetailView):
    model = Employee

    def get_queryset(self):
        return super(EmployeeDetailView, self).get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetailView, self).get_context_data(**kwargs)
        context['exams'] = self.object.exams.select_related()
        context['updated'] = Exam.objects.aggregate(upd_date=Max('modified'))['upd_date']
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


class EmployeeListView(ListView):
    model = Employee


class TerritoryListView(ListView):
    model = Territory


class TerritoryDetailView(DetailView):
    model = Territory


class PlaceListView(ListView):
    model = Place


class PlaceDetailView(DetailView):
    model = Place


class ExamDetailView(DetailView):
    model = Exam


class IndexView(View):

    def get(self, request):
        db_update()
        # initial_db_populate()
        return HttpResponse("It's work!")
