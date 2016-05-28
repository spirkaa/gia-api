from django.db import models
import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import ExamDate, ExamLevel, Organisation, Position, Employee, Territory, Place, Exam


class EmployeeFilter(django_filters.FilterSet):

    org__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Место работы')
    position = django_filters.ModelChoiceFilter(
        queryset=Position.objects.all(),
        label='Должность в ППЭ')

    class Meta:
        model = Employee

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'get'
        helper.form_class = 'form-horizontal'
        helper.form_id = 'filter'
        helper.layout = Layout(
            'name',
            'org__name',
            'position',
            Submit('filter', 'Найти'))
        return helper


class PlaceFilter(django_filters.FilterSet):

    code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Код ППЭ')
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Наименование ППЭ')
    addr = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Адрес ППЭ')
    ate__code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Код АТЕ')
    ate__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Наименование АТЕ')

    class Meta:
        model = Place

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'get'
        helper.form_class = 'form-horizontal'
        helper.form_id = 'filter'
        helper.layout = Layout(
            'code',
            'name',
            'addr',
            'ate__code',
            'ate__name',
            Submit('filter', 'Найти'))
        return helper


class ExamFilter(django_filters.FilterSet):

    date = django_filters.ModelChoiceFilter(
        queryset=ExamDate.objects.all(),
        label='Дата экзамена')
    level = django_filters.ModelChoiceFilter(
        queryset=ExamLevel.objects.all(),
        label='Уровень')
    place__code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Код ППЭ')
    place__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название ППЭ')
    place__addr = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Адрес ППЭ')
    employee__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='ФИО сотрудника')
    employee__org__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Место работы')

    filter_overrides = {
        models.CharField: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'lookup_type': 'icontains'
            }
        },
    }

    class Meta:
        model = Exam

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'get'
        helper.form_class = 'form-horizontal'
        helper.form_id = 'filter'
        helper.layout = Layout(
            'date',
            'level',
            'employee__name',
            'employee__org__name',
            'place__code',
            'place__name',
            'place__addr',
            Submit('filter', 'Найти'))
        return helper
