

from django.utils.translation import ugettext_lazy as _


class CVVError(Exception):
    def __init__(self):
        self.message = _(u'CVV Error, please check and try again')
        super(CVVError, self).__init__()

class CARDError(Exception):
    def __init__(self):
        self.message = _(u'Card Error, please check and try again')

class OLDCARDError(Exception):
    def __init__(self):
        self.message = _(u'Your card has expired')

class ERR_TBK_CARD(Exception):
    def __init__(self):
        self.message = _(u'Wrong card type, please check and try again')

class ERR_TBK_NUMBER_QUOTAS(Exception):
    def __init__(self):
        self.message = _(u'Quota error, wrong number of cuotes, please check and try again')

class ERR_TBK_NUMBER_CARD(Exception):
    def __init__(self):
        self.message = _(u'Card Error, wrong number, please check and try again')

class ERR_TBK_CVV(Exception):
    def __init__(self):
        self.message = _(u'CVV Error, please check and try again')

class ERR_TIMEOUT(Exception):
    def __init__(self):
        self.message = _(u'Time limit exedeed, please check and try again')

class ERR_RUT(Exception):
    def __init__(self):
        self.message = _(u'Rut Error, please check and try again')

class ERR_CCV(Exception):
    def __init__(self):
        self.message = _(u'Security code error')

class ERR_EXPIRATION_DATE(Exception):
    def __init__(self):
        self.message = _(u'Error in the expiration date')

class ERR_AMOUNT(Exception):
    def __init__(self):
        self.message = _(u'Amount error')

class SOAPException(Exception):

    exceptions = {
        25: ERR_EXPIRATION_DATE(),
        33: ERR_AMOUNT(),
        52: CARDError(),
        86: OLDCARDError(),
        109: ERR_TBK_CARD(),
        111: ERR_TBK_NUMBER_QUOTAS(),
        112: ERR_TBK_NUMBER_CARD(),
        115: ERR_TBK_CVV(),
        272: ERR_TIMEOUT(),
        285: ERR_RUT()
    }

    def __init__(self, error_code):

        self.__generic_msg = \
            _("The possible causes of this rejection are:") \
            _("- Failure to enter the data of your Credit or Debit card (date and / or security code).")\
            _("- Your credit or debit card does not have enough balance.") \
            _("- Card not yet enabled in the financial system.")

        self.message = self.__generic_msg
        self.__error_code = error_code

    def __call__(self):
        if self.exceptions.get(self.__error_code, None) is not None:
            return self.exceptions[self.__error_code]
        return self
