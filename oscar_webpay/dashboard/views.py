from django.views import generic
from django.conf import settings

from oscar_webpay import models


class TransactionListView(generic.ListView):
    model = models.WebPayTransaction
    template_name = 'oscar_webpay/dashboard/transaction_list.html'
    context_object_name = 'transactions'



class TransactionDetailView(generic.DetailView):
    model = models.WebPayTransaction
    template_name = 'oscar_webpay/dashboard/transaction_detail.html'
    context_object_name = 'txn'

    def get_context_data(self, **kwargs):
        ctx = super(TransactionDetailView, self).get_context_data(**kwargs)
        return ctx