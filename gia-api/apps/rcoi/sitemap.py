from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Employee, Organisation


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            "rcoi:home",
            "rcoi:exam",
            "rcoi:employee",
            "rcoi:organisation_list",
            "rcoi:place",
        ]

    def location(self, obj):
        return reverse(obj)


class ConfiguredSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 5000

    def lastmod(self, obj):
        return obj.modified


class EmployeeSitemap(ConfiguredSitemap):
    def items(self):
        return Employee.objects.all()


class OrganisationSitemap(ConfiguredSitemap):
    def items(self):
        return Organisation.objects.all()


sitemaps_context = {
    "static": StaticSitemap,
    "organisation": OrganisationSitemap,
    "employee": EmployeeSitemap,
}
