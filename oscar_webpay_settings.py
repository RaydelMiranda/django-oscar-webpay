from django.conf import settings
from django.conf import LazyObject

from django.utils.translation import ugettext_lazy as _

import os


class OscarWebpaySettingError(Exception):
    pass


class OscarWebpaySettings(object):

    def __init__(self):

        self.WEBPAY_RETURN_IP_ADDRESS = getattr(settings, 'WEBPAY_RETURN_IP_ADDRESS', '127.0.0.1')
        self.WEBPAY_RETURN_PORT = getattr(settings, 'WEBPAY_RETURN_PORT', 80)
        self.WEBPAY_CERT_DIR = getattr(settings, 'WEBPAY_CERT_DIR', os.path.join(settings.BASE_DIR, 'webpay_certificates'))
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
                    raise OscarWebpaySettingError(
                        _(u'You must set the configuration for all the enabled webpay modes\n'
                          u'Please configure WEBPAY_{} setting\'s variable.'.format(mode))
                    )
                else:
                    setattr(self, 'WEBPAY_{}'.format(mode), webpay_mode)

                # Check all the required data is set.
                for key in self.__conf_required_data:
                    if key not in webpay_mode.keys():
                        raise OscarWebpaySettingError(_(u'WEBPAY_{} "{}" setting has not been set.').format(mode, key))
            else:
                raise OscarWebpaySettingError(_(u'Oscar webpay do not support this mode: {}'.format(mode)))


class OscarWebpayLazySettings(LazyObject):

    def _setup(self, name=None):
        self._wrapped = OscarWebpaySettings()


oscar_webpay_settings = OscarWebpayLazySettings()
