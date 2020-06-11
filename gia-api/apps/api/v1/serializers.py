from django.db.models import Count
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.rcoi import models


class DateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Date
        fields = ("id", "date")


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Level
        fields = ("id", "level")


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organisation
        fields = ("id", "name")


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Position
        fields = ("id", "name")


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Place
        fields = ("id", "code", "name", "addr")


class EmployeeSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()

    class Meta:
        model = models.Employee
        fields = ("id", "name", "org")


class ExamSerializer(serializers.ModelSerializer):
    date = DateSerializer()
    level = LevelSerializer()
    place = PlaceSerializer()
    position = PositionSerializer()
    employee = EmployeeSerializer()

    class Meta:
        model = models.Exam
        exclude = ("created", "modified")


class ExamFlatSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source="date.date")
    level = serializers.CharField(source="level.level")
    code = serializers.CharField(source="place.code")
    place = serializers.CharField(source="place.name")
    addr = serializers.CharField(source="place.addr")
    position = serializers.CharField(source="position.name")
    employee = serializers.CharField(source="employee.name")
    org = serializers.CharField(source="employee.org.name")

    class Meta:
        model = models.Exam
        exclude = ("created", "modified")


class ExamFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exam
        fields = "__all__"
        depth = 2


class ExamForEmployeeSerializer(serializers.ModelSerializer):
    date = DateSerializer()
    level = LevelSerializer()
    position = PositionSerializer()
    place = PlaceSerializer()

    class Meta:
        model = models.Exam
        exclude = ("created", "modified", "employee")


class EmployeeDetailSerializer(serializers.ModelSerializer):
    org = OrganisationSerializer()
    exams = ExamForEmployeeSerializer(many=True)

    class Meta:
        model = models.Employee
        depth = 1
        fields = ("id", "name", "org", "exams")


class EmployeeForOrgSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    org = serializers.IntegerField(source="org_id")
    num_exams = serializers.IntegerField(read_only=True)
    exams = ExamForEmployeeSerializer(many=True)


class EmployeesAnnotatedField(serializers.Field):
    def to_representation(self, value):
        s = (
            value.annotate(num_exams=Count("exams"))
            .prefetch_related(
                "exams__date",
                "exams__level",
                "exams__place",
                "exams__place__ate",
                "exams__position",
            )
            .order_by("name")
            .all()
        )
        ser = EmployeeForOrgSerializer(s, many=True)
        return ser.data


class OrganisationDetailSerializer(serializers.ModelSerializer):
    employees = EmployeesAnnotatedField(read_only=True)

    class Meta:
        model = models.Organisation
        fields = ("id", "name", "employees")


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        exclude = ("created", "modified")


class DataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataFile
        exclude = ("created", "modified")


def limit_subscriptions(fields):
    limit = 100
    if fields["user"].subscriptions.count() == limit:
        raise serializers.ValidationError(
            "У вас не может быть больше {} подписок".format(limit)
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Subscription
        fields = ("id", "user", "employee")
        validators = [
            UniqueTogetherValidator(
                queryset=models.Subscription.objects.all(),
                fields=("user", "employee"),
                message="Вы уже подписаны на этого сотрудника",
            ),
            limit_subscriptions,
        ]


class SubscriptionListSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = models.Subscription
        fields = ("id", "employee")


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    employee = EmployeeDetailSerializer()

    class Meta:
        model = models.Subscription
        fields = ("id", "employee")
