from rest_framework import serializers
from . import models


class DateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Date
        fields = (
            'id', 
            'date', 
        )


class LevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Level
        fields = (
            'id', 
            'level', 
        )


class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Organisation
        fields = (
            'id', 
            'name', 
        )


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Position
        fields = (
            'id', 
            'name', 
        )


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Employee
        fields = (
            'id', 
            'name', 
        )


class TerritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Territory
        fields = (
            'slug', 
            'code', 
            'name', 
        )


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Place
        fields = (
            'slug', 
            'code', 
            'name', 
            'addr', 
        )


class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Exam
        fields = (
            'id', 
        )
