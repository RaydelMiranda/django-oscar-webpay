"""
Copyright (2017) Raydel Miranda 

This file is part of Django Oscar Webpay.

    Django Oscar Webpay is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Django Oscar Webpay is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Django Oscar Webpay.  If not, see <http://www.gnu.org/licenses/>.
"""

class CertificateConf(object):
    @staticmethod
    def get_conf_from_setting(webpay_setting):
        """
        Get a dictionary with the certificate configuration for a specific environment
        (E.g. PRODUCTION, INTEGRATION, etc ...)
        
        :param webpay_setting: Configuration for the webpay payment method.
        :return: A dict containing the certificate configuration as required by
                 the functions in the API provided by TransBank.
        """
        certificate = dict({})

        certificate.update({
            'environment': webpay_setting['ACTIVE_ENVIRON'],
            'private_key': webpay_setting['PRIVATE_KEY'],
            'public_cert': webpay_setting['PUBLIC_CERT'],
            'webpay_cert': webpay_setting['WEBPAY_CERT'],
            'commerce_code': webpay_setting['COMMERCE_CODE']
        })

        return certificate
