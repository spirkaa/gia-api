from django.db.models import Count
from rest_framework import serializers

from apps.rcoi import models


class DateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Date
        fields = ('id',
                  'date')


class LevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Level
        fields = ('id',
                  'level')


class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Organisation
        fields = ('id',
                  'name')

    def to_representation(self, instance):
        from apps.rcoi.templatetags.rename import rename_org
        data = super(OrganisationSerializer, self).to_representation(instance)
        data.update({'name': rename_org(data['name'])})
        return data


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Position
        fields = ('id',
                  'name')


class TerritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Territory
        fields = ('id',
                  'code',
                  'name')


class PlaceSerializer(serializers.ModelSerializer):
    ate = TerritorySerializer()

    class Meta:
        model = models.Place
        fields = ('id',
                  'code',
                  'name',
                  'addr',
                  'ate')

    def to_representation(self, instance):
        from apps.rcoi.templatetags.rename import rename_org
        data = super(PlaceSerializer, self).to_representation(instance)
        data.update({'name': rename_org(data['name'])})
        return data


class EmployeeSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()

    class Meta:
        model = models.Employee
        fields = ('id',
                  'name',
                  'org')


class ExamSerializer(serializers.ModelSerializer):
    date = DateSerializer()
    level = LevelSerializer()
    place = PlaceSerializer()
    position = PositionSerializer()
    employee = EmployeeSerializer()

    class Meta:
        model = models.Exam
        exclude = ('created',
                   'modified')


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
        exclude = ('created',
                   'modified')

    def to_representation(self, instance):
        from apps.rcoi.templatetags.rename import rename_org
        data = super(ExamFlatSerializer, self).to_representation(instance)
        data.update({'place': rename_org(data['place'])})
        return data


class ExamFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Exam
        depth = 2


class ExamForEmployeeSerializer(serializers.ModelSerializer):
    date = DateSerializer()
    level = LevelSerializer()
    position = PositionSerializer()
    place = PlaceSerializer()

    class Meta:
        model = models.Exam
        exclude = ('created',
                   'modified',
                   'employee')


class EmployeeDetailSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()
    exams = ExamForEmployeeSerializer(many=True)

    class Meta:
        model = models.Employee
        depth = 1
        fields = ('id',
                  'name',
                  'org',
                  'exams')


class EmployeeForOrgSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    org = serializers.IntegerField(source='org_id')
    num_exams = serializers.IntegerField(read_only=True)
    exams = ExamForEmployeeSerializer(many=True)


class EmployeesAnnotatedField(serializers.Field):
    def to_representation(self, value):
        s = value\
            .annotate(num_exams=Count('exams'))\
            .prefetch_related('exams__date',
                              'exams__level',
                              'exams__place',
                              'exams__place__ate',
                              'exams__position')\
            .all()
        ser = EmployeeForOrgSerializer(s, many=True)
        return ser.data


class OrganisationDetailSerializer(serializers.ModelSerializer):
    employees = EmployeesAnnotatedField(read_only=True)

    class Meta:
        model = models.Organisation
        fields = ('id',
                  'name',
                  'employees')

    def to_representation(self, instance):
        from apps.rcoi.templatetags.rename import rename_org
        data = super(OrganisationDetailSerializer, self).to_representation(instance)
        data.update({'name': rename_org(data['name'])})
        return data
