import datetime
from calendar import timegm

from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sites.requests import RequestSite
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import http_date

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


class EmployeeSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 5000

    def items(self):
        return Employee.objects.all()

    def lastmod(self, obj):
        return obj.modified


class OrganisationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 5000

    def items(self):
        return Organisation.objects.all()

    def lastmod(self, obj):
        return obj.modified


@x_robots_tag
def index(
    request,
    sitemaps,
    template_name="sitemap_index.xml",
    content_type="application/xml",
    sitemap_url_name="django.contrib.sitemaps.views.sitemap",
):

    req_protocol = request.scheme
    req_site = RequestSite(request)

    sites = []
    for section, site in sitemaps.items():
        if callable(site):
            site = site()
        protocol = req_protocol if site.protocol is None else site.protocol
        sitemap_url = reverse(sitemap_url_name, kwargs={"section": section})
        absolute_url = "%s://%s%s" % (protocol, req_site.domain, sitemap_url)
        sites.append(absolute_url)
        for page in range(2, site.paginator.num_pages + 1):
            sites.append("%s?p=%s" % (absolute_url, page))

    return TemplateResponse(
        request, template_name, {"sitemaps": sites}, content_type=content_type
    )


@x_robots_tag
def sitemap(
    request,
    sitemaps,
    section=None,
    template_name="sitemap.xml",
    content_type="application/xml",
):

    req_protocol = request.scheme
    req_site = RequestSite(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    lastmod = None
    all_sites_lastmod = True
    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=page, site=req_site, protocol=req_protocol))
            if all_sites_lastmod:
                site_lastmod = getattr(site, "latest_lastmod", None)
                if site_lastmod is not None:
                    site_lastmod = (
                        site_lastmod.utctimetuple()
                        if isinstance(site_lastmod, datetime.datetime)
                        else site_lastmod.timetuple()
                    )
                    lastmod = (
                        site_lastmod if lastmod is None else max(lastmod, site_lastmod)
                    )
                else:
                    all_sites_lastmod = False
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    response = TemplateResponse(
        request, template_name, {"urlset": urls}, content_type=content_type
    )
    if all_sites_lastmod and lastmod is not None:
        # if lastmod is defined for all sites, set header so as
        # ConditionalGetMiddleware is able to send 304 NOT MODIFIED
        response["Last-Modified"] = http_date(timegm(lastmod))
    return response


sitemaps_context = {
    "static": StaticSitemap,
    "organisation": OrganisationSitemap,
    "employee": EmployeeSitemap,
}
