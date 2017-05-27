from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, ListView
from django_tables2 import RequestConfig

from .filters import EmployeeFilter, PlaceFilter, ExamFilter
from .models import DataSource, DataFile, Date, Level, Organisation, Position, Employee, Territory, Place, Exam, RcoiUpdater
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
        context['sources'] = DataSource.objects.all()
        context['updated'] = DataFile.objects.latest('modified').modified
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
        context['sources'] = DataSource.objects.all()
        context['updated'] = DataFile.objects.latest('modified').modified
        return context


class EmployeeDetailView(DetailView):
    model = Employee

    def get_queryset(self):
        return super(EmployeeDetailView, self).get_queryset().select_related()

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetailView, self).get_context_data(**kwargs)
        context['exams'] = self.object.exams.select_related()
        context['sources'] = DataSource.objects.all()
        context['updated'] = DataFile.objects.latest('modified').modified
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


@staff_member_required
def update_db_view(request):
    if request.method == 'POST':
        # noinspection PyBroadException
        try:
            updated = RcoiUpdater().run()
            if updated:
                messages.info(request, 'База данных обновлена!')
            else:
                messages.info(request, 'Изменений нет!')
        except:
            messages.error(request, 'Ошибка!')
    return redirect(reverse('admin:index'))


@staff_member_required
def clear_caches_view(request):
    from django.conf import settings

    if settings.DEBUG:
        messages.warning(request, 'Эта кнопка работает только на продакшене!')
    else:
        if request.method == 'POST':
            # noinspection PyBroadException
            try:
                from cacheops import invalidate_all
                from django.core.cache import cache
                invalidate_all()
                cache.clear()
                messages.info(request, 'Кэш очищен!')
            except:
                messages.error(request, 'Ошибка!')
    return redirect(reverse('admin:index'))
