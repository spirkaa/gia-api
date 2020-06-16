import datetime

import pytest
from ddf import G
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from apps.rcoi import models

pytestmark = pytest.mark.django_db


def test_datasource_str():
    """
    Test Model - DataSource - String representation
    """
    test = "test"
    obj = G(models.DataSource, name=test)
    assert obj.__str__() == test


def test_datafile_str():
    """
    Test Model - DataFile - String representation
    """
    test = "test"
    obj = G(models.DataFile, name=test)
    assert obj.__str__() == test


def test_date_str():
    """
    Test Model - Date - String representation
    """
    test = datetime.datetime(2017, 5, 1)
    obj = G(models.Date, date=test)
    assert obj.__str__() == str(test)


def test_level_str():
    """
    Test Model - Level - String representation
    """
    test = "11"
    obj = G(models.Level, level=test)
    assert obj.__str__() == test


def test_organisation_str():
    """
    Test Model - Organisation - String representation
    """
    test = "test"
    obj = G(models.Organisation, name=test)
    assert obj.__str__() == test


def test_position_str():
    """
    Test Model - Position - String representation
    """
    test = "test"
    obj = G(models.Position, name=test)
    assert obj.__str__() == test


def test_employee_str():
    """
    Test Model - Employee - String representation
    """
    test = "test"
    obj = G(models.Employee, name=test, org__name="school")
    assert obj.__str__() == test
    assert obj.org.name == "school"


def test_place_str():
    """
    Test Model - Place - String representation
    """
    test = "test"
    obj = G(models.Place, name=test)
    assert obj.__str__() == test


def test_exam_str():
    """
    Test Model - Exam - String representation
    """
    date = datetime.datetime(2017, 5, 1)
    place = "school"
    employee = "test"
    test_str = str(date) + ", " + place + ", " + employee
    obj = G(models.Exam, date__date=date, place__name=place, employee__name=employee,)
    assert obj.__str__() == test_str


def test_subscription_str():
    """
    Test Model - Subscription - String representation
    """
    user = "user"
    employee = "test"
    test_str = user + " --> " + employee
    obj = G(models.Subscription, user__username=user, employee__name=employee,)
    assert obj.__str__() == test_str


def test_date_get_absolute_url():
    """
    Test Model - Date - Object Details URL
    """
    obj = G(models.Date)
    assert obj.get_absolute_url() == reverse("rcoi:date_detail", args=(obj.id,))


def test_date_get_update_url():
    """
    Test Model - Date - Object Update URL (not implemented)
    """
    obj = G(models.Date)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_level_get_absolute_url():
    """
    Test Model - Level - Object Details URL
    """
    obj = G(models.Level)
    assert obj.get_absolute_url() == reverse("rcoi:level_detail", args=(obj.id,))


def test_level_get_update_url():
    """
    Test Model - Level - Object Update URL (not implemented)
    """
    obj = G(models.Level)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_organisation_get_absolute_url():
    """
    Test Model - Organisation - Object Details URL
    """
    obj = G(models.Organisation)
    assert obj.get_absolute_url() == reverse("rcoi:organisation_detail", args=(obj.id,))


def test_organisation_get_update_url():
    """
    Test Model - Organisation - Object Update URL (not implemented)
    """
    obj = G(models.Organisation)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_position_get_absolute_url():
    """
    Test Model - Position - Object Details URL
    """
    obj = G(models.Position)
    assert obj.get_absolute_url() == reverse("rcoi:position_detail", args=(obj.id,))


def test_position_get_update_url():
    """
    Test Model - Position - Object Update URL (not implemented)
    """
    obj = G(models.Position)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_employee_get_absolute_url():
    """
    Test Model - Employee - Object Details URL
    """
    obj = G(models.Employee)
    assert obj.get_absolute_url() == reverse("rcoi:employee_detail", args=(obj.id,))


def test_employee_get_update_url():
    """
    Test Model - Employee - Object Update URL (not implemented)
    """
    obj = G(models.Employee)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_place_get_absolute_url():
    """
    Test Model - Place - Object Details URL
    """
    obj = G(models.Place)
    assert obj.get_absolute_url() == reverse("rcoi:place_detail", args=(obj.id,))


def test_place_get_update_url():
    """
    Test Model - Place - Object Update URL (not implemented)
    """
    obj = G(models.Place)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()


def test_exam_get_absolute_url():
    """
    Test Model - Exam - Object Details URL
    """
    obj = G(models.Exam)
    assert obj.get_absolute_url() == reverse("rcoi:exam_detail", args=(obj.id,))


def test_exam_get_update_url():
    """
    Test Model - Exam - Object Update URL (not implemented)
    """
    obj = G(models.Exam)
    with pytest.raises(NoReverseMatch):
        assert obj.get_update_url()
