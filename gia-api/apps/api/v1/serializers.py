from django.db.models import Count
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.rcoi import models


class DateSerializer(serializers.ModelSerializer):
    """Serializer for Date model."""

    class Meta:
        model = models.Date
        fields = ("id", "date")


class LevelSerializer(serializers.ModelSerializer):
    """Serializer for Level model."""

    class Meta:
        model = models.Level
        fields = ("id", "level")


class OrganisationSerializer(serializers.ModelSerializer):
    """Serializer for Organisation model."""

    class Meta:
        model = models.Organisation
        fields = ("id", "name")


class PositionSerializer(serializers.ModelSerializer):
    """Serializer for Position model."""

    class Meta:
        model = models.Position
        fields = ("id", "name")


class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for Place model."""

    class Meta:
        model = models.Place
        fields = ("id", "code", "name", "addr")


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model."""

    org = OrganisationSerializer()

    class Meta:
        model = models.Employee
        fields = ("id", "name", "org")


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model."""

    date = DateSerializer()
    level = LevelSerializer()
    place = PlaceSerializer()
    position = PositionSerializer()
    employee = EmployeeSerializer()

    class Meta:
        model = models.Exam
        exclude = ("created", "modified")


class ExamFlatSerializer(serializers.ModelSerializer):
    """Serializer for Exam model with fields flattened."""

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
    """Serializer for Exam model with nested fields included."""

    class Meta:
        model = models.Exam
        fields = "__all__"
        depth = 2


class ExamForEmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Exam to be included in Employee."""

    date = DateSerializer()
    level = LevelSerializer()
    position = PositionSerializer()
    place = PlaceSerializer()

    class Meta:
        model = models.Exam
        exclude = ("created", "modified", "employee")


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer for Employee detail."""

    org = OrganisationSerializer()
    exams = ExamForEmployeeSerializer(many=True)

    class Meta:
        model = models.Employee
        depth = 1
        fields = ("id", "name", "org", "exams")


class EmployeeForOrgSerializer(serializers.Serializer):
    """Serializer for Employee to be included in Organisation."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    org = serializers.IntegerField(source="org_id")
    num_exams = serializers.IntegerField(read_only=True)
    exams = ExamForEmployeeSerializer(many=True)


class EmployeesAnnotatedField(serializers.Field):
    """Annotated list of employees with exams."""

    def to_representation(self, value):
        s = (
            value.annotate(num_exams=Count("exams"))
            .prefetch_related(
                "exams__date",
                "exams__level",
                "exams__place",
                "exams__position",
            )
            .order_by("name")
            .all()
        )
        ser = EmployeeForOrgSerializer(s, many=True)
        return ser.data


class OrganisationDetailSerializer(serializers.ModelSerializer):
    """Serializer for Organisation detail."""

    employees = EmployeesAnnotatedField(read_only=True)

    class Meta:
        model = models.Organisation
        fields = ("id", "name", "employees")


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""

    class Meta:
        model = models.DataSource
        exclude = ("created", "modified")


class DataFileSerializer(serializers.ModelSerializer):
    """Serializer for DataFile model."""

    class Meta:
        model = models.DataFile
        exclude = ("created", "modified")


def limit_subscriptions(fields):
    """Limit number of subscriptions per user."""
    limit = 100
    if fields["user"].subscriptions.count() == limit:
        msg = f"У вас не может быть больше {limit} подписок"
        raise serializers.ValidationError(msg)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""

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
    """Serializer for Subscription list."""

    employee = EmployeeSerializer()

    class Meta:
        model = models.Subscription
        fields = ("id", "employee")


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    """Serializer for Subscription detail."""

    employee = EmployeeDetailSerializer()

    class Meta:
        model = models.Subscription
        fields = ("id", "employee")
