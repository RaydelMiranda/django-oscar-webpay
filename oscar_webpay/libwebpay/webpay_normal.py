"""
@author     Allware Ltda. (http://www.allware.cl)
@copyright  2016 Transbank S.A. (http://www.tranbank.cl)
@date       Jan 2015
@license    GNU LGPL
@version    2.0.1
"""

from django.http import HttpResponse
import socket

from oscar_webpay.certificates import cert_normal

from suds.client import Client
from suds.cache import NoCache
from suds.wsse import Security, Timestamp
from wsse.suds import WssePlugin

from suds.transport.https import HttpTransport
import logging

logging.basicConfig()

config = None
url = None;

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar_webpay.oscar_webpay_settings import OscarWebpaySettingError

from wsse.exceptions import  SignatureVerificationFailed

from logging import getLogger

logger = getLogger('oscar_webpay.transactions')


class Dictionaries():
    """
	Configuracion de WSDL segun ambiente
	"""

    @staticmethod
    def dictionaryConfig():
        normal_config = getattr(settings, 'WEBPAY_NORMAL', None)
        config = normal_config.get('ENVIRONMENTS', None)
        if config is None:
            raise OscarWebpaySettingError(_('You must provide the ENVIRONMENTS variable for the settings'))

        return config

class WebpayNormal():
    def __init__(self, configuration):
        global config;
        config = configuration;
        self.__config = config

        dictWsdl = Dictionaries.dictionaryConfig();

        global url;
        url = dictWsdl[self.__config.getEnvironment()];
        self.__url = url;

    @staticmethod
    def log_webpay_traffic(client, msg=""):
        logger.info("\n{}\n".format('='*100))
        logger.info(client.last_sent())
        logger.info("\n{}\n".format('='*100))
        logger.info(client.last_received())

    """
	initTransaction
	
	Permite inicializar una transaccion en Webpay. 
	Como respuesta a la invocacion se genera un token que representa en forma unica una transaccion.
	"""

    @staticmethod
    def initTransaction(amount, buyOrder, sessionId, urlReturn, urlFinal):
        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert())
        #client.options.cache.clear()
        init = client.factory.create('wsInitTransactionInput')

        init.wSTransactionType = client.factory.create('wsTransactionType').TR_NORMAL_WS

        init.commerceId = config.getCommerceCode();

        init.buyOrder = buyOrder;
        init.sessionId = sessionId;
        init.returnURL = urlReturn;
        init.finalURL = urlFinal;

        detail = client.factory.create('wsTransactionDetail');
        detail.amount = amount;

        detail.commerceCode = config.getCommerceCode();
        detail.buyOrder = buyOrder;

        init.transactionDetails.append(detail);
        init.wPMDetail = client.factory.create('wpmDetailInput');

        try:
            wsInitTransactionOutput = client.service.initTransaction(init);
        except SignatureVerificationFailed as e:
            raise
        WebpayNormal.log_webpay_traffic(client)

        return wsInitTransactionOutput;


    """
	getTransaction
	
	Permite obtener el resultado de la transaccion una vez que 
	Webpay ha resuelto su autorizacion financiera.
	"""

    @staticmethod
    def getTransaction(token):
        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert());
        #client.options.cache.clear();
        transactionResultOutput = client.service.getTransactionResult(token);
        # acknowledge = WebpayNormal.acknowledgeTransaction(token);

        WebpayNormal.log_webpay_traffic(client)
        return transactionResultOutput;

    def acknowledgeTransaction(self, token):
        acknowledge = WebpayNormal.acknowledgeTransaction(token);

        return acknowledge

    """
	acknowledgeTransaction
	Indica  a Webpay que se ha recibido conforme el resultado de la transaccion
	"""

    @staticmethod
    def acknowledgeTransaction(token):
        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert());
        #client.options.cache.clear();

        acknowledge = client.service.acknowledgeTransaction(token);
        WebpayNormal.log_webpay_traffic(client)

        return acknowledge;

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
            ], cache=NoCache()
        )
