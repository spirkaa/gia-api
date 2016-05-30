from rest_framework import viewsets, permissions
from . import models
from . import serializers


class ExamDateViewSet(viewsets.ModelViewSet):
    """ViewSet for the ExamDate class"""

    queryset = models.Date.objects.all()
    serializer_class = serializers.DateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamLevelViewSet(viewsets.ModelViewSet):
    """ViewSet for the ExamLevel class"""

    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrganisationViewSet(viewsets.ModelViewSet):
    """ViewSet for the Organisation class"""

    queryset = models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Position class"""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for the Employee class"""

    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


class TerritoryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Territory class"""

    queryset = models.Territory.objects.all()
    serializer_class = serializers.TerritorySerializer
    permission_classes = [permissions.IsAuthenticated]


class PlaceViewSet(viewsets.ModelViewSet):
    """ViewSet for the Place class"""

    queryset = models.Place.objects.all()
    serializer_class = serializers.PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for the Exam class"""

    queryset = models.Exam.objects.all()
    serializer_class = serializers.ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
