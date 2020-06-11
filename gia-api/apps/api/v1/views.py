from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import DetailSerializerMixin

from apps.rcoi import models

from . import filters, serializers
from .permissions import IsOwner


class DateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Date class"""

    queryset = models.Date.objects.all()
    serializer_class = serializers.DateSerializer
    filterset_class = filters.DateFilter


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Level class"""

    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
    filterset_class = filters.LevelFilter


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Position class"""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    filterset_class = filters.PositionFilter


class OrganisationViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Organisation class"""

    queryset = models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    serializer_detail_class = serializers.OrganisationDetailSerializer
    filterset_class = filters.OrganisationFilter


class EmployeeViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Employee class"""

    queryset = models.Employee.objects.select_related()
    queryset_detail = queryset.prefetch_related(
        "exams__date",
        "exams__level",
        "exams__place",
        "exams__place__ate",
        "exams__position",
    ).all()
    serializer_class = serializers.EmployeeSerializer
    serializer_detail_class = serializers.EmployeeDetailSerializer
    filterset_class = filters.EmployeeFilter


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Place class"""

    queryset = models.Place.objects.select_related()
    serializer_class = serializers.PlaceSerializer
    filterset_class = filters.PlaceFilter


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Exam class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamSerializer
    filterset_class = filters.ExamFilter


class ExamFlatViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ExamFlat class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamFlatSerializer
    filterset_class = filters.ExamFilter


class ExamFullViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ExamFull class"""

    queryset = models.Exam.objects.select_related()
    serializer_class = serializers.ExamFullSerializer
    filterset_class = filters.ExamFilter


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the DataSource class"""

    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer


class DataFileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the DataFile class"""

    queryset = models.DataFile.objects.all()
    serializer_class = serializers.DataFileSerializer


@method_decorator(never_cache, name="dispatch")
class SubscriptionViewSet(viewsets.GenericViewSet):
    """ ViewSet for managing User to Employee subscriptions """

    swagger_schema = None

    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = self.request.user.subscriptions.all().select_related()
        queryset = queryset.prefetch_related(
            "employee__exams__date",
            "employee__exams__level",
            "employee__exams__place",
            "employee__exams__position",
        ).all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {"Location": data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.SubscriptionDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.SubscriptionDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()
