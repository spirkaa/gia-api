from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.views import generic
from django.views.generic import TemplateView, DetailView, ListView, View
from django_tables2 import RequestConfig
from .models import Date, Level, Organisation, Position, Employee, Territory, Place, Exam
from .filters import EmployeeFilter, PlaceFilter, ExamFilter
from .tables import EmployeeTable, PlaceTable, ExamTable
from django.http import HttpResponse
from .models import initial_db_populate


class EmployeeTableView(TemplateView):
    template_name = 'rcoi/employee.html'

    def get_queryset(self, **kwargs):
        return Employee.objects.select_related().all()

    def get_context_data(self, **kwargs):
        context = super(EmployeeTableView, self).get_context_data(**kwargs)
        filter = EmployeeFilter(self.request.GET,
                                queryset=self.get_queryset(**kwargs))
        filter.form.helper = EmployeeFilter().helper
        table = EmployeeTable(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        last_update = Exam.objects.latest('modified')
        context['last_update'] = last_update.modified
        return context


class PlaceTableView(TemplateView):
    template_name = 'rcoi/place.html'

    def get_queryset(self, **kwargs):
        return Place.objects.select_related().all()

    def get_context_data(self, **kwargs):
        context = super(PlaceTableView, self).get_context_data(**kwargs)
        filter = PlaceFilter(self.request.GET,
                                queryset=self.get_queryset(**kwargs))
        filter.form.helper = PlaceFilter().helper
        table = PlaceTable(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        last_update = Exam.objects.latest('modified')
        context['last_update'] = last_update.modified
        return context


class ExamTableView(TemplateView):
    template_name = 'rcoi/exam.html'

    def get_queryset(self, **kwargs):
        return Exam.objects.select_related().all()

    def get_context_data(self, **kwargs):
        context = super(ExamTableView, self).get_context_data(**kwargs)
        filter = ExamFilter(self.request.GET,
                            queryset=self.get_queryset(**kwargs))
        filter.form.helper = ExamFilter().helper
        table = ExamTable(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        last_update = Exam.objects.latest('modified')
        context['last_update'] = last_update.modified
        return context


# class ExamListView(ListView):
#     model = Exam
#     paginate_by = 50
#
#     def get_context_data(self, **kwargs):
#         context = super(ExamListView, self).get_context_data(**kwargs)
#         exams = Exam.objects.select_related().all()
#         paginator = Paginator(exams, self.paginate_by)
#         page = self.request.GET.get('page')
#         try:
#             exams = paginator.page(page)
#         except PageNotAnInteger:
#             exams = paginator.page(1)
#         except EmptyPage:
#             exams = paginator.page(paginator.num_pages)
#
#         context['exams'] = exams
#         return context


class ExamDateListView(ListView):
    model = Date


class ExamDateDetailView(DetailView):
    model = Date


class ExamLevelListView(ListView):
    model = Level


class ExamLevelDetailView(DetailView):
    model = Level


class OrganisationListView(ListView):
    model = Organisation


class OrganisationDetailView(DetailView):
    model = Organisation

    def get_queryset(self):
        return super(OrganisationDetailView, self).get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetailView, self).get_context_data(**kwargs)
        context['employees'] = self.object.employees.select_related()
        last_update = Exam.objects.latest('modified')
        context['last_update'] = last_update.modified
        return context


class PositionListView(ListView):
    model = Position


class PositionDetailView(DetailView):
    model = Position


class EmployeeListView(ListView):
    model = Employee


class EmployeeDetailView(DetailView):
    model = Employee

    def get_queryset(self):
        return super(EmployeeDetailView, self).get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetailView, self).get_context_data(**kwargs)
        context['exams'] = self.object.exams.select_related()
        last_update = Exam.objects.latest('modified')
        context['last_update'] = last_update.modified
        return context


class TerritoryListView(ListView):
    model = Territory


class TerritoryDetailView(DetailView):
    model = Territory


class PlaceListView(ListView):
    model = Place


class PlaceDetailView(DetailView):
    model = Place


class ExamListView(ListView):
    model = Exam


class ExamDetailView(DetailView):
    model = Exam


class IndexView(View):

    def get(self, request):
        initial_db_populate()
        return HttpResponse("It's work!")
