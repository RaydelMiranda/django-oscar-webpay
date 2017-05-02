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