from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model


CoreTransaction = get_model('payment', 'Transaction')

class WebPayTransaction(CoreTransaction):
    token = models.CharField(_(u"Token"), max_length=255)
    error_code = models.IntegerField(_(u"Error code"))
    error_message = models.CharField(_(u"Error message"), max_length=255, default=u"-")
    method = models.CharField(_(u"Methods"), max_length=50)