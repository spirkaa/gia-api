from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from allauth import app_settings
from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

if TYPE_CHECKING:
    from allauth.account.models import EmailConfirmation
    from django.http import HttpRequest


def build_absolute_uri(
    request: HttpRequest | None, location: str, protocol: str | None = None
) -> str:
    """request.build_absolute_uri() helper.

    Like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    if request is None:
        if not app_settings.SITES_ENABLED:
            msg = "Passing `request=None` requires `sites` to be enabled."
            raise ImproperlyConfigured(msg)

        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = f"{account_settings.DEFAULT_HTTP_PROTOCOL}://{site.domain}{location}"
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)
    # NOTE: We only force a protocol if we are instructed to do so
    # (via the `protocol` parameter, or, if the default is set to
    # HTTPS. The latter keeps compatibility with the debatable use
    # case of running your site under both HTTP and HTTPS, where one
    # would want to make sure HTTPS links end up in password reset
    # mails even while they were initiated on an HTTP password reset
    # form.
    if not protocol and account_settings.DEFAULT_HTTP_PROTOCOL == "https":
        protocol = account_settings.DEFAULT_HTTP_PROTOCOL
    # (end NOTE)
    if protocol:
        uri = f"{protocol}:{uri.partition(':')[2]}"
    return uri


class SitesDomainAccountAdapter(DefaultAccountAdapter):
    """Account adapter with support for custom domains."""

    def get_email_confirmation_url(
        self, request: HttpRequest, emailconfirmation: EmailConfirmation
    ):
        """Construct the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        return build_absolute_uri(None, url)
