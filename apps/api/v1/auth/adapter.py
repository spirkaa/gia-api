from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri


class AnotherDomainAccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse(
            "account_confirm_email",
            args=[emailconfirmation.key])
        ret = build_absolute_uri(
            None,
            url,
            protocol='https')
        return ret

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = 'api/v1/auth/email_confirmation_signup'
        else:
            email_template = 'api/v1/auth/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)
