"""
@author     Allware Ltda. (http://www.allware.cl)
@copyright  2016 Transbank S.A. (http://www.tranbank.cl)
@date       Jan 2015
@license    GNU LGPL
@version    2.0.1
"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
import socket

from oscar_webpay.certificates import cert_normal

from suds.client import Client
from suds.wsse import Security, Timestamp
from wsse.suds import WssePlugin

from suds.transport.https import HttpTransport
import logging

from oscar_webpay.oscar_webpay_settings import OscarWebpaySettingError

logging.basicConfig()

config = None
url = None



class Dictionaries():
    """
	Configuracion de WSDL segun ambiente
	"""

    @staticmethod
    def dictionaryConfig():
        normal_config = getattr(settings, 'WEBPAY_NORMAL_MALL', None)
        config = normal_config.get('ENVIRONMENTS', None)
        if config is None:
            raise OscarWebpaySettingError(_('You must provide the ENVIRONMENTS variable for the settings'))

        return config


class WebpayMallNormal():
    def __init__(self, configuration):

        global config
        config = configuration
        self.__config = config

        dictWsdl = Dictionaries.dictionaryConfig()

        global url
        url = dictWsdl[self.__config.getEnvironment()]
        self.__url = url

    """
	initTransaction
	
	Permite inicializar una transaccion en Webpay. 
	Como respuesta a la invocacion se genera un token que representa en forma unica una transaccion.
	"""

    @staticmethod
    def initTransaction(amount, buyOrder, sessionId, urlReturn, urlFinal, stores):

        client = WebpayMallNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(),
                                             config.getWebPayCert())
        client.options.cache.clear()

        init = client.factory.create('wsInitTransactionInput')

        init.wSTransactionType = client.factory.create('wsTransactionType').TR_MALL_WS

        init.commerceId = config.getCommerceCode()

        init.buyOrder = buyOrder
        init.sessionId = sessionId
        init.returnURL = urlReturn
        init.finalURL = urlFinal

        for data in stores:
            detail = client.factory.create('wsTransactionDetail')

            detail.commerceCode = data[0]
            detail.buyOrder = data[1]
            detail.amount = data[2]

            init.transactionDetails.append(detail)

        try:
            wsInitTransactionOutput = client.service.initTransaction(init)
        except Exception as e:
            str(e)

        return wsInitTransactionOutput

    """
	getTransaction
	
	Permite obtener el resultado de la transaccion una vez que 
	Webpay ha resuelto su autorizacion financiera.
	"""

    @staticmethod
    def getTransaction(token):

        client = WebpayMallNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(),
                                             config.getWebPayCert())
        client.options.cache.clear()

        transactionResultOutput = client.service.getTransactionResult(token)
        acknowledge = WebpayMallNormal.acknowledgeTransaction(token)

        return transactionResultOutput

    """
	acknowledgeTransaction
	Indica  a Webpay que se ha recibido conforme el resultado de la transaccion
	"""

    @staticmethod
    def acknowledgeTransaction(token):

        client = WebpayMallNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(),
                                             config.getWebPayCert())
        client.options.cache.clear()

        acknowledge = client.service.acknowledgeTransaction(token)

        return acknowledge

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
