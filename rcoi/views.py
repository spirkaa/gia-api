from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
from django_tables2 import RequestConfig
from .models import Employee, Place, Exam
from .filters import EmployeeFilter, PlaceFilter, ExamFilter
from .tables import EmployeeTable, PlaceTable, ExamTable
from django.http import HttpResponse
from .models import db_populate


class EmployeeTableView(generic.TemplateView):
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
        return context


class PlaceTableView(generic.TemplateView):
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
        return context


class ExamTableView(generic.TemplateView):
    template_name = 'rcoi/index.html'

    def get_queryset(self, **kwargs):
        return Exam.objects.select_related().all()
        # return Exam.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ExamTableView, self).get_context_data(**kwargs)
        filter = ExamFilter(self.request.GET,
                            queryset=self.get_queryset(**kwargs))
        filter.form.helper = ExamFilter().helper
        table = ExamTable(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        return context


class ListView(generic.ListView):
    model = Exam
    template_name = 'rcoi/list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        exams = Exam.objects.select_related().all()
        paginator = Paginator(exams, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            exams = paginator.page(page)
        except PageNotAnInteger:
            exams = paginator.page(1)
        except EmptyPage:
            exams = paginator.page(paginator.num_pages)

        context['exams'] = exams
        return context


# class IndexView(generic.View):
#
#     def get(self, request):
#         # db_populate()
#         return HttpResponse("It's work!")
