"""
Copyright (2017) Raydel Miranda 

This file is part of Django Oscar Webpay.

    Django Oscar Webpay is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Django Oscar Webpay is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Django Oscar Webpay.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar_webpay.oscar_webpay_settings import OscarWebpaySettingError

from suds.client import Client
from suds.wsse import Security
from wsse.suds import WssePlugin

from suds.transport.https import HttpTransport
import logging

logging.basicConfig()

config = None
url = None


class Dictionaries(object):
    """
    Configuring WSDL according environment.
    """

    @staticmethod
    def dictionary_config():
        normal_config = getattr(settings, 'WEBPAY_NORMAL', None)
        env_config = normal_config.get('ENVIRONMENTS', None)
        if env_config is None:
            raise OscarWebpaySettingError(_('You must provide the ENVIRONMENTS variable for the settings'))
        return env_config


class WebpayNormal(object):
    def __init__(self, configuration):
        global config
        config = configuration
        self.__config = config

        dictWsdl = Dictionaries.dictionary_config()

        global url
        url = dictWsdl[self.__config.getEnvironment()]
        self.__url = url

    @staticmethod
    def init_transaction(amount, buy_order, session_id, url_return, url_final):
        """
        initTransaction
        
        Permite inicializar una transaccion en Webpay. 
        Como respuesta a la invocacion se genera un token que representa en forma unica una transaccion.
        """

        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert())
        client.options.cache.clear()
        init = client.factory.create('wsInitTransactionInput')

        init.wSTransactionType = client.factory.create('wsTransactionType').TR_NORMAL_WS

        init.commerceId = config.getCommerceCode()

        init.buyOrder = buy_order
        init.sessionId = session_id
        init.returnURL = url_return
        init.finalURL = url_final

        detail = client.factory.create('wsTransactionDetail')
        detail.amount = amount

        detail.commerceCode = config.getCommerceCode()
        detail.buyOrder = buy_order

        init.transactionDetails.append(detail)
        init.wPMDetail = client.factory.create('wpmDetailInput')

        wsInitTransactionOutput = client.service.init_transaction(init)

        return wsInitTransactionOutput

    @staticmethod
    def get_transaction(token):
        """
        getTransaction
        
        Permite obtener el resultado de la transaccion una vez que 
        Webpay ha resuelto su autorizacion financiera.
        """

        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert())
        client.options.cache.clear()
        transactionResultOutput = client.service.getTransactionResult(token)
        # acknowledge = WebpayNormal.acknowledgeTransaction(token)
        return transactionResultOutput

    def acknowledge_transaction(self, token):  # noqa
        acknowledge = WebpayNormal.acknowledge_transaction(token)
        return acknowledge

    @staticmethod
    def acknowledge_transaction(token):
        """
        acknowledgeTransaction
        Indica  a Webpay que se ha recibido conforme el resultado de la transaccion
        """

        client = WebpayNormal.get_client(url, config.getPrivateKey(), config.getPublicCert(), config.getWebPayCert())
        client.options.cache.clear()

        acknowledge = client.service.acknowledge_transaction(token)

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
