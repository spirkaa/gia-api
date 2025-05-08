from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from django.urls import reverse


class SitesDomainAccountAdapter(DefaultAccountAdapter):
    """Account adapter with support for custom domains."""

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Construct the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        return build_absolute_uri(None, url)
