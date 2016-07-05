from django.db.models import Count
from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin
from rcoi import models
from . import serializers
from . import filters


class DateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Date class"""

    queryset = models.Date.objects.all()
    serializer_class = serializers.DateSerializer
    filter_class = filters.DateFilter


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Level class"""

    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
    filter_class = filters.LevelFilter


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Position class"""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    filter_class = filters.LevelFilter


class OrganisationViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Organisation class"""

    queryset = models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    serializer_detail_class = serializers.OrganisationDetailSerializer
    filter_class = filters.OrganisationFilter


class EmployeeViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Employee class"""

    queryset = models.Employee.objects.select_related()
    queryset_detail = queryset.prefetch_related('exams__date',
                                                'exams__level',
                                                'exams__place',
                                                'exams__place__ate',
                                                'exams__position').all()
    serializer_class = serializers.EmployeeSerializer
    serializer_detail_class = serializers.EmployeeDetailSerializer
    filter_class = filters.EmployeeFilter


class TerritoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Territory class"""

    queryset = models.Territory.objects.all()
    serializer_class = serializers.TerritorySerializer
    filter_class = filters.TerritoryFilter


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Place class"""

    queryset = models.Place.objects.all()
    serializer_class = serializers.PlaceSerializer
    filter_class = filters.PlaceFilter


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Exam class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamSerializer
    filter_class = filters.ExamFilter


class ExamFlatViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ExamFlat class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamFlatSerializer
    filter_class = filters.ExamFilter


class ExamFullViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ExamFull class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamFullSerializer
    filter_class = filters.ExamFilter
