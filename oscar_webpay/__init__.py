import os
import logging
from oscar.defaults import OSCAR_DASHBOARD_NAVIGATION

from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger('oscar_webpay')


OSCAR_DASHBOARD_NAVIGATION += (
    {
        'label': _('WebPay'),
        'icon': 'icon-globe',
        'children': [
            {
                'label': _('WebPay transactions'),
                'url_name': 'webpay-transaction-list',
            },
        ]
    },
)