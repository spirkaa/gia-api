import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from . import models


class FilterWithHelper(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super(FilterWithHelper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.form_show_labels = False
        self.helper.form_id = 'filter'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'


class EmployeeFilter(FilterWithHelper):

    def __init__(self, *args, **kwargs):
        super(EmployeeFilter, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'name',
            'org__name',
            Submit('filter', 'Найти'))

    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='ФИО сотрудника')
    org__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Место работы')

    class Meta:
        model = models.Employee
        fields = '__all__'


class PlaceFilter(FilterWithHelper):

    def __init__(self, *args, **kwargs):
        super(PlaceFilter, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'code',
            'name',
            'addr',
            Submit('filter', 'Найти'))

    code = django_filters.CharFilter(
        label='Код ППЭ')
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Наименование ППЭ')
    addr = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Адрес ППЭ')

    class Meta:
        model = models.Place
        fields = '__all__'


class ExamFilter(FilterWithHelper):

    def __init__(self, *args, **kwargs):
        super(ExamFilter, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'date',
            'level',
            'place__code',
            'place__name',
            'place__addr',
            'employee__name',
            'employee__org__name',
            Submit('filter', 'Найти'))

    date = django_filters.ModelChoiceFilter(
        queryset=models.Date.objects.all(),
        label='Дата экзамена')
    level = django_filters.ModelChoiceFilter(
        queryset=models.Level.objects.all(),
        label='Уровень')
    place__code = django_filters.CharFilter(
        label='Код ППЭ')
    place__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Наименование ППЭ')
    place__addr = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Адрес ППЭ')
    employee__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='ФИО сотрудника')
    employee__org__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Место работы')

    class Meta:
        model = models.Exam
        fields = '__all__'
