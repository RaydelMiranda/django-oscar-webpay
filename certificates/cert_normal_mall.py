"""
  @author     Allware Ltda. (http://www.allware.cl)
  @copyright  2015 Transbank S.A. (http://www.tranbank.cl)
  @date       Jan 2015
  @license    GNU LGPL
  @version    2.0.1
"""

import os

from oscar_webpay.oscar_webpay_settings import oscar_webpay_settings


class certDictionary():
    @staticmethod
    def dictionaryCert():
        certificate = dict()

        dir = os.path.dirname(__file__)

        """ ATENCION: Configurar modo de uso (INTEGRACION, CERTIFICACION o PRODUCCION) """
        certificate['environment'] = oscar_webpay_settings.WEBPAY_NOMRAL_MALL['ENVIRON']

        """ Llave Privada: Configura tu ruta absoluta """
        certificate['private_key'] = oscar_webpay_settings.WEBPAY_NOMRAL_MALL['PRIVATE_KEY']

        """ Certificado Publico: Configura tu ruta absoluta """
        certificate['public_cert'] = oscar_webpay_settings.WEBPAY_NOMRAL_MALL['PUBLIC_CERT']

        """ Certificado Privado: COnfigura tu ruta absoluta """
        certificate['webpay_cert'] = oscar_webpay_settings.WEBPAY_NOMRAL_MALL['WEBPAY_CERT']

        """ Codigo Comercio """
        certificate['commerce_code'] = oscar_webpay_settings.WEBPAY_NOMRAL_MALL['COMMERCE_CODE']

        return certificate

    @staticmethod
    def store_codes():
        store_codes = dict()

        """ Tienda 1 """
        store_codes['tienda1'] = '597020000543'

        """ Tienda 2 """
        store_codes['tienda2'] = '597020000544'

        return store_codes
