from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from oscar.core.loading import get_model


Transaction = get_model('payment', 'Transaction')
CoreSource = get_model('payment', 'Source')


class WebPayTransaction(models.Model):

    base_transaction = GenericRelation(Transaction)

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

    # In oscar transactions this attribute points to 'payment.Source',
    # we need to point to our source class.

    token = models.CharField(_(u"Token"), max_length=255)
    buy_order = models.CharField(_(u"Buy order number"), max_length=26)
    commerce_code = models.CharField(_(u"Commerce code"), max_length=12)
    installments_amount = models.FloatField(_(u"Installments amount"))
    currency = models.CharField(_(u"Currency"), max_length=3)
    auth_code = models.CharField(_(u"Authorization code"), max_length=6, null=True)
    card_number = models.CharField(_(u"Card number"), max_length=4, null=True)

    error_auth_code = models.CharField(_(u"Error code"), max_length=3, choices=TRANSACTION_ERROR_CODE_CHOICES, null=True)
    transaction_type = models.CharField(_(u"Transaction type"), max_length=255, choices=TRANSACTION_TYPE_CHOICES, null=True)

    def method(self):
        return _("WebPay: {}".format(self.transaction_type.display()))

    def get_absolute_url(self):
        return reverse('webpay-transaction-detail', kwargs={'pk': str(self.pk)})


class WebPaySource(CoreSource):
    def __init__(self, *args, **kwargs):
        super(CoreSource, self).__init__(*args, **kwargs)
        self.deferred_txns_webpay_data = None

    def save(self, *args, **kwargs):
        super(CoreSource, self).save(*args, **kwargs)
        if self.deferred_txns:
            for txn in self.deferred_txns:
                # Reference is at index 2 in the txn arg list
                reference = txn[2]
                self._create_transaction(*txn, webpay_transaction_data=self.deferred_txns_webpay_data[reference])

    def create_deferred_transaction(self, txn_type, amount, reference=None,
                                    status=None, token=None, buy_order=None, commerce_code=None,
                                    installments_amount=None, currency=None, auth_code=None, card_number=None,
                                    error_auth_code=None, transaction_type=None):
        """
        Register the data for a transaction that can't be created yet due to FK
        constraints.  This happens at checkout where create an payment source
        and a transaction but can't save them until the order model exists.
        
        This function overwrites the original in order to add additional webpay transaction data.
        
        """

        super(WebPaySource, self).create_deferred_transaction(txn_type, amount, reference, status)

        if self.deferred_txns_webpay_data is None:
            self.deferred_txns_webpay_data = {}

        self.deferred_txns_webpay_data.update(
            {
                reference: {
                    'token': token,
                    'buy_order': buy_order,
                    'commerce_code': commerce_code,
                    'installments_amount': installments_amount.incl_tax,
                    'currency': currency,
                    'auth_code': auth_code,
                    'card_number': card_number,
                    'error_auth_code': error_auth_code,
                    'transaction_type': transaction_type
                }
            }
        )

    def _create_transaction(self, txn_type, amount, reference='',
                            status='', webpay_transaction_data=None):

        wp_txn = None

        if webpay_transaction_data is not None:
            wp_txn = WebPayTransaction.objects.create(**webpay_transaction_data)

        txn = self.transactions.create(
            transaction_data=wp_txn,
            txn_type=txn_type, amount=amount,
            reference=reference, status=status)
