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

from django.conf.urls import url

from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class WebPayApplication(DashboardApplication):
    name = None
    default_permissions = ['is_staff', ]

    transaction_list = get_class('oscar_webpay.dashboard.views', 'TransactionListView')
    transaction_detail = get_class('oscar_webpay.dashboard.views', 'TransactionDetailView')

    def get_urls(self):
        urls = [
            url(r'^transactions/$', self.transaction_list.as_view(), name='webpay-transaction-list'),
            url(r'^transactions/(?P<pk>\d+)$', self.transaction_detail.as_view(),
                name='webpay-transaction-detail'),
        ]
        return self.post_process_urls(urls)


application = WebPayApplication()