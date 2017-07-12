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

import logging
import os

from django.conf import settings
from django.conf import LazyObject
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger('oscar_webpay')


class OscarWebpaySettingError(Exception):
    pass


class OscarWebpaySettings(object):

    def __init__(self):

        # As oscar payment flow is defined, an order is only placed after payment
        # completion. Set `PLACE_ORDER_BEFORE_TAKE_PAYMENT` to True in order to
        # place an order BEFORE payment submission.
        # This can be handy when you want to track client payment intents, even if payment fails.
        self.PLACE_ORDER_BEFORE_TAKE_PAYMENT = getattr(settings, 'PLACE_ORDER_BEFORE_TAKE_PAYMENT', False)
        # If `PLACE_ORDER_BEFORE_TAKE_PAYMENT` is set to True, you might want yo define a
        # status for such order.
        self.ORDER_STATUS_BEFORE_PAYMENT = getattr(settings, 'ORDER_STATUS_BEFORE_PAYMENT', _(u"Pending payment"))

        self.WEBPAY_RETURN_IP_ADDRESS = getattr(settings, 'WEBPAY_RETURN_IP_ADDRESS', '127.0.0.1')
        self.WEBPAY_RETURN_PORT = getattr(settings, 'WEBPAY_RETURN_PORT', 80)
        self.WEBPAY_CERT_DIR = getattr(settings, 'WEBPAY_CERT_DIR', os.path.join(settings.BASE_DIR,
                                                                                 'webpay_certificates'))
        self.WEBPAY_ENABLED_MODES = getattr(settings, 'WEBPAY_ENABLED_MODES', ['NORMAL'])
        self.__webpay_modes = ['NORMAL', 'NORMAL_MALL', 'CAPTURE', 'ONECLICK', 'COMPLETE', 'NULLIFY']
        self.__conf_required_data = [
            'ACTIVE_ENVIRON',   # Use mode (INTEGRATION, CERTIFICATION o PRODUCTION).
            'ENVIRONMENTS',     # Dictionary, keys are environment and values are the WSDL values.
            'PRIVATE_KEY',      # Private key, absolute path.
            'PUBLIC_CERT',      # Public certificate, absolute path.
            'WEBPAY_CERT',      # Private cert, absolute path.
            'COMMERCE_CODE',    # Well ...   Commerce code ;)
        ]

        for mode in self.WEBPAY_ENABLED_MODES:
            if mode in self.__webpay_modes:
                webpay_mode = getattr(settings, 'WEBPAY_{}'.format(mode), None)
                if webpay_mode is None:
                    error_msg = _(u'You must set the configuration for all the enabled webpay modes\n' \
                                  u'Please configure WEBPAY_{} setting\'s variable.'.format(mode))
                    logger.error(error_msg)
                    raise OscarWebpaySettingError(error_msg)
                else:
                    setattr(self, 'WEBPAY_{}'.format(mode), webpay_mode)

                # Check all the required data is set.
                for key in self.__conf_required_data:
                    if key not in webpay_mode.keys():
                        error_msg = _(u'WEBPAY_{} "{}" setting has not been set.').format(mode, key)
                        logger.error(error_msg)
                        raise OscarWebpaySettingError(error_msg)
            else:
                error_msg = _(u'Oscar webpay do not support this mode: {}'.format(mode))
                logger.error(error_msg)
                raise OscarWebpaySettingError(error_msg)


class OscarWebpayLazySettings(LazyObject):

    def _setup(self, name=None):
        self._wrapped = OscarWebpaySettings()


oscar_webpay_settings = OscarWebpayLazySettings()
