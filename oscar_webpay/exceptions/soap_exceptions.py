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

class SOAPException(Exception):

    exceptions = {
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
        self.__error_code = error_code

    def __call__(self):
        return self.exceptions[self.__error_code]
