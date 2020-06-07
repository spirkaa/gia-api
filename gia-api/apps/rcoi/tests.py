import datetime

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse

from .models import (
    DataFile,
    DataSource,
    Date,
    Employee,
    Exam,
    Level,
    Organisation,
    Place,
    Position,
    Subscription,
)


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {"username": "username", "email": "username@tempurl.com"}
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {"name": "group"}
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_datasource(**kwargs):
    defaults = {"name": "name", "url": "http://example.com"}
    defaults.update(**kwargs)
    return DataSource.objects.create(**defaults)


def create_datafile(**kwargs):
    defaults = {
        "name": "name",
        "url": "http://example.com",
        "size": 0,
        "last_modified": datetime.datetime.now(),
    }
    defaults.update(**kwargs)
    return DataFile.objects.create(**defaults)


def create_date(**kwargs):
    defaults = {"date": datetime.datetime.now()}
    defaults.update(**kwargs)
    return Date.objects.create(**defaults)


def create_level(**kwargs):
    defaults = {"level": "11"}
    defaults.update(**kwargs)
    return Level.objects.create(**defaults)


def create_organisation(**kwargs):
    defaults = {"name": "name"}
    defaults.update(**kwargs)
    return Organisation.objects.create(**defaults)


def create_position(**kwargs):
    defaults = {"name": "name"}
    defaults.update(**kwargs)
    return Position.objects.create(**defaults)


def create_employee(**kwargs):
    defaults = {"name": "name"}
    defaults.update(**kwargs)
    if "org" not in defaults:
        defaults["org"] = create_organisation()
    return Employee.objects.create(**defaults)


def create_place(**kwargs):
    defaults = {
        "code": "code",
        "name": "name",
        "addr": "addr",
    }
    defaults.update(**kwargs)
    return Place.objects.create(**defaults)


def create_exam(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    if "date" not in defaults:
        defaults["date"] = create_date()
    if "level" not in defaults:
        defaults["level"] = create_level()
    if "place" not in defaults:
        defaults["place"] = create_place()
    if "employee" not in defaults:
        defaults["employee"] = create_employee()
    if "position" not in defaults:
        defaults["position"] = create_position()
    if "datafile" not in defaults:
        defaults["datafile"] = create_datafile()
    return Exam.objects.create(**defaults)


def create_subscription(**kwargs):
    defaults = {"last_send": datetime.datetime(2017, 5, 1)}
    defaults.update(**kwargs)
    if "user" not in defaults:
        defaults["user"] = create_django_contrib_auth_models_user()
    if "employee" not in defaults:
        defaults["employee"] = create_employee()
    return Subscription.objects.create(**defaults)


class DateViewTest(TestCase):
    """
    Tests for Date
    """

    def setUp(self):
        self.client = Client()

    def test_list_date(self):
        url = reverse("rcoi:date_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_date(self):
        date = create_date()
        url = reverse("rcoi:date_detail", args=[date.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class LevelViewTest(TestCase):
    """
    Tests for Level
    """

    def setUp(self):
        self.client = Client()

    def test_list_level(self):
        url = reverse("rcoi:level_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_level(self):
        level = create_level()
        url = reverse("rcoi:level_detail", args=[level.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class OrganisationViewTest(TestCase):
    """
    Tests for Organisation
    """

    def setUp(self):
        self.client = Client()
        create_datafile()

    def test_list_organisation(self):
        url = reverse("rcoi:organisation_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_organisation(self):
        organisation = create_organisation()
        url = reverse("rcoi:organisation_detail", args=[organisation.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PositionViewTest(TestCase):
    """
    Tests for Position
    """

    def setUp(self):
        self.client = Client()

    def test_list_position(self):
        url = reverse("rcoi:position_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_position(self):
        position = create_position()
        url = reverse("rcoi:position_detail", args=[position.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class EmployeeViewTest(TestCase):
    """
    Tests for Employee
    """

    def setUp(self):
        self.client = Client()
        create_datafile(url="http://EmployeeViewTest.com")

    def test_list_employee(self):
        url = reverse("rcoi:employee")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_employee(self):
        employee = create_employee()
        url = reverse("rcoi:employee_detail", args=[employee.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PlaceViewTest(TestCase):
    """
    Tests for Place
    """

    def setUp(self):
        self.client = Client()
        create_datafile(url="http://PlaceViewTest.com")

    def test_list_place(self):
        url = reverse("rcoi:place")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_place(self):
        place = create_place()
        url = reverse("rcoi:place_detail", args=[place.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ExamViewTest(TestCase):
    """
    Tests for Exam
    """

    def setUp(self):
        self.client = Client()
        create_datafile(url="http://ExamViewTest.com")

    def test_list_exam(self):
        url = reverse("rcoi:exam")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_exam(self):
        exam = create_exam()
        url = reverse("rcoi:exam_detail", args=[exam.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
