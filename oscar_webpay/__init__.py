"""
Copyright (2017) Raydel Miranda 

This file is part of Django Oscar WebPay.

    Django Oscar WebPay is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Django Oscar WebPay is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Django Oscar WebPay.  If not, see <http://www.gnu.org/licenses/>.
"""

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