from apps.rcoi.middleware import SetBrowserCacheTimeoutMiddleware


def dummy_get_response(request):
    return None


def test_dummy_get_response():
    assert dummy_get_response("test") is None


def test_set_browser_cache_timeout_middleware(settings, max_age_response):
    """
    Test middleware - set response header
    """
    max_age = settings.RESPONSE_CACHE_SECONDS = 123
    middleware = SetBrowserCacheTimeoutMiddleware(dummy_get_response)
    r = middleware.process_response(None, max_age_response)
    assert r["cache-control"] == f"max-age={max_age}"
