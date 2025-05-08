from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def navactive(request, urls):
    """Check if url presents in request path.

    :type request: request
    :param request: request
    :type urls: str
    :param urls: urls
    :return: css class name
    :rtype: str

    {% navactive request 'rcoi:employee' %}
    """
    for path in [reverse(url) for url in urls.split()]:
        if path in request.path:
            return "active"
    return ""
