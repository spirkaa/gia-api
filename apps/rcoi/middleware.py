import time

from django.conf import settings
from django.utils.cache import get_max_age, patch_cache_control
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import http_date


class SetBrowserCacheTimeoutMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        max_age = int(settings.RESPONSE_CACHE_SECONDS)
        current_max_age = get_max_age(response)
        if current_max_age:
            max_age = min(current_max_age, max_age)
        response["Expires"] = http_date(time.time() + max_age)
        patch_cache_control(response, max_age=max_age)
        return response
