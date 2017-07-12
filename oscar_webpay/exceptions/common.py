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

from django.utils.translation import ugettext_lazy as _


class MissingShippingMethodException(Exception):

    def __init__(self, value):
        self.message = _(u"Shipping method expected, received: {}".format(value))


class MissingShippingAddressException(Exception):

    def __init__(self, value):
        self.message = _(u"Shipping address expected, received: {}".format(value))


class TransactionException(Exception):

    def __init__(self, *args, **kwargs):
        super(TransactionException, *args, **kwargs)


class AuthenticationError(TransactionException):
    pass


class FailedTransaction(TransactionException):

    def __init__(self, cause=None, *args, **kwargs):
        self.message = _(u'Failed transaction motive: {}'.format(cause if cause else _(u'Unknown')))
        super(FailedTransaction, self).__init__(*args, **kwargs)


class TimeLimitExceeded(TransactionException):
    pass


class AbortedTransactionByCardHolder(TransactionException):
    pass


class U3Exception(TransactionException):
    """ Internal error. """
    pass
