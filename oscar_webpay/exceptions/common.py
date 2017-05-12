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
