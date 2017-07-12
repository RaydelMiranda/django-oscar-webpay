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

from django.views import generic

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
