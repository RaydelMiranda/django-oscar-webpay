from oscar_webpay.libwebpay.webpay import Webpay
from oscar_webpay.certificates import cert_normal
from oscar_webpay.libwebpay.configuration import Configuration

from oscar_webpay.oscar_webpay_settings import oscar_webpay_settings
from django.core.urlresolvers import reverse


def get_webpay_conf():
    certificate = cert_normal.certDictionary.dictionaryCert()
    configuration = Configuration()
    configuration.setEnvironment(certificate['environment'])
    configuration.setCommerceCode(certificate['commerce_code'])
    configuration.setPrivateKey(certificate['private_key'])
    configuration.setPublicCert(certificate['public_cert'])
    configuration.setWebpayCert(certificate['webpay_cert'])
    return configuration


def get_webpay_client(order_number, total):

    webpay = Webpay(get_webpay_conf())

    amount = total
    buy_order = order_number
    session_id = None

    final_url = 'http://{}:{}{}'.format(
        oscar_webpay_settings.WEBPAY_RETURN_IP_ADDRESS,
        oscar_webpay_settings.WEBPAY_RETURN_PORT,
        reverse('webpay-fail')
    )

    return_url = 'http://{}:{}{}'.format(
        oscar_webpay_settings.WEBPAY_RETURN_IP_ADDRESS,
        oscar_webpay_settings.WEBPAY_RETURN_PORT,
        reverse('webpay-details')
    )

    client = webpay.getNormalTransaction().initTransaction(amount, buy_order, session_id, return_url, final_url)
    return client


def confirm_transaction(token):
    webpay = Webpay(get_webpay_conf())
    return webpay.getNormalTransaction().getTransaction(token)


