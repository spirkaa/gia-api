from rest_framework import serializers
from rcoi import models


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


class OrganisationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Organisation
        fields = (
            'id',
            'name',
            'employees'
        )
        depth = 1


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Position
        fields = (
            'id',
            'name',
        )


class TerritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Territory
        fields = (
            'id',
            'code',
            'name',
        )


class PlaceSerializer(serializers.ModelSerializer):
    ate = TerritorySerializer()

    class Meta:
        model = models.Place
        fields = (
            'id',
            'code',
            'name',
            'addr',
            'ate'
        )


class EmployeeSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()

    class Meta:
        model = models.Employee
        fields = ('id', 'name', 'org',)


class ExamSerializer(serializers.ModelSerializer):
    date = DateSerializer()
    level = LevelSerializer()
    place = PlaceSerializer()
    position = PositionSerializer()
    employee = EmployeeSerializer()

    class Meta:
        model = models.Exam
        exclude = ('created', 'modified')


class ExamFlatSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date.date')
    level = serializers.CharField(source='level.level')
    code = serializers.CharField(source='place.code')
    place = serializers.CharField(source='place.name')
    addr = serializers.CharField(source='place.addr')
    position = serializers.CharField(source='position.name')
    employee = serializers.CharField(source='employee.name')
    org = serializers.CharField(source='employee.org.name')

    class Meta:
        model = models.Exam
        exclude = ('created', 'modified')


class ExamFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Exam
        depth = 2


class ExamForEmployeeSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='date.date')
    position = serializers.CharField(source='position.name')
    place = serializers.CharField(source='place.name')
    addr = serializers.CharField(source='place.addr')

    class Meta:
        model = models.Exam
        exclude = ('created', 'modified', 'level', 'employee')


class EmployeeDetailSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()
    exams = ExamForEmployeeSerializer(many=True)

    class Meta:
        model = models.Employee
        fields = ('id', 'name', 'org', 'exams',)
        depth = 1
