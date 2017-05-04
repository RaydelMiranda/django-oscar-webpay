from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model


CoreTransaction = get_model('payment', 'Transaction')

class WebPayTransaction(CoreTransaction):

    TRANSACTION_TYPE_CHOICES = (
        ('VD', _(u'Debit sale')),
        ('VN', _(u'Normal sale')),
        ('VC', _(u'Quota sale')),
        ('SI', _(u'3 non-interest installments')),
        ('S2', _(u'2 non-interest installments')),
        ('NC', _(u'N non-interes installments'))
    )

    TRANSACTION_ERROR_CODE_CHOICES = (
        ('TSY', _(u"Successful transaction")),
        ('TSN', _(u"Failed transaction")),
        ('TO', _(u"Time limit exceeded")),
        ('ABO', _(u"Transaction aborted by card holder")),
        ('U3', _(u"Authentication internal error")),
    )

    token = models.CharField(_(u"Token"), max_length=255)
    buy_order = models.CharField(_(u"Buy order number"), max_length=26)
    commerce_code = models.CharField(_(u"Commerce code"), max_length=12)
    installments_amount = models.IntegerField(_(u"Installments amount"))
    currency = models.CharField(_(u"Currency"), max_length=3)
    auth_code = models.CharField(_(u"Authorization code"), max_length=6)
    card_number = models.CharField(_(u"Card number"), max_length=4)

    error_auth_code = models.IntegerField(_(u"Error code"), choices=TRANSACTION_ERROR_CODE_CHOICES)
    transaction_type = models.CharField(_(u"Transaction type"), max_length=255, choices=TRANSACTION_TYPE_CHOICES)

    def method(self):
        return _("WebPay: {}".format(self.transaction_type.display()))

