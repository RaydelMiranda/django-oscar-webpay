"""
@author     Allware Ltda. (http://www.allware.cl)
@copyright  2016 Transbank S.A. (http://www.tranbank.cl)
@date       Jan 2015
@license    GNU LGPL
@version    2.0.1
"""
from django.conf import settings
from django.http import HttpResponse
import socket

from certificates import cert_capture

from suds.client import Client
from suds.wsse import Security, Timestamp
from wsse.suds import WssePlugin

from suds.transport.https import HttpTransport
import logging

from decimal import *

from oscar_webpay.oscar_webpay_settings import OscarWebpaySettingError
from django.utils.translation import ugettext_lazy as _

logging.basicConfig()

config = None
url = None


class Dictionaries():
    """
	Configuracion de WSDL segun ambiente
	"""

    @staticmethod
    def dictionaryConfig():
        normal_config = getattr(settings, 'WEBPAY_CAPTURE', None)
        config = normal_config.get('ENVIRONMENTS', None)
        if config is None:
            raise OscarWebpaySettingError(_('You must provide the ENVIRONMENTS variable for the settings'))

        return config


class WebpayCapture():
    def __init__(self, configuration):

        global config
        config = configuration
        self.__config = config

        dictWsdl = Dictionaries.dictionaryConfig()

        global url
        url = dictWsdl[self.__config.getEnvironment()]
        self.__url = url

    """
		El metodo capture debe ser invocado siempre indicando el codigo del comercio que realizo la 
		transaccion. En el caso de comercios MALL, el codigo debe ser el codigo de la tienda virtual. 
		"""

    @staticmethod
    def capture(authorizationCode, captureAmount, buyOrder):

        client = WebpayCapture.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert())

        client.options.cache.clear()

        captureInput = client.factory.create('captureInput')

        captureInput.commerceId = config.getCommerceCode()
        captureInput.authorizationCode = authorizationCode
        captureInput.buyOrder = buyOrder
        captureInput.captureAmount = captureAmount

        try:
            captureOuput = client.service.capture(captureInput)
        except Exception as e:
            print str(e)

        return captureOuput

    @staticmethod
    def get_client(wsdl_url, our_keyfile_path, our_certfile_path, their_certfile_path):

        transport = HttpTransport()
        wsse = Security()

        return Client(
            wsdl_url,
            transport=transport,
            wsse=wsse,
            plugins=[
                WssePlugin(
                    keyfile=our_keyfile_path,
                    certfile=our_certfile_path,
                    their_certfile=their_certfile_path,
                ),
            ],
        )
