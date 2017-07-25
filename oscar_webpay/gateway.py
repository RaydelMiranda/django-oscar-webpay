from oscar_webpay.libwebpay.webpay import Webpay
from oscar_webpay.certificates import cert_normal
from oscar_webpay.libwebpay.configuration import Configuration

from oscar_webpay.oscar_webpay_settings import oscar_webpay_settings
from oscar_webpay.exceptions import \
    AuthenticationError, \
    FailedTransaction, \
    AbortedTransactionByCardHolder, \
    TimeLimitExceeded, \
    U3Exception

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


def get_webpay_client(order_number, total, return_url_name, final_url_name):

    webpay = Webpay(get_webpay_conf())

    amount = total
    buy_order = order_number
    session_id = None

    final_url = '{}:{}{}'.format(
        oscar_webpay_settings.WEBPAY_RETURN_IP_ADDRESS,
        oscar_webpay_settings.WEBPAY_RETURN_PORT,
        reverse(final_url_name)
    )

    return_url = '{}:{}{}'.format(
        oscar_webpay_settings.WEBPAY_RETURN_IP_ADDRESS,
        oscar_webpay_settings.WEBPAY_RETURN_PORT,
        reverse(return_url_name)
    )

    initTransactionOutput = webpay.getNormalTransaction().initTransaction(amount, buy_order, session_id, return_url, final_url)
    return initTransactionOutput


def confirm_transaction(token):
    webpay = Webpay(get_webpay_conf())
    result = webpay.getNormalTransaction().getTransaction(token)

    if result.VCI == 'TSY':
        # Successful transaction.
        pass

    if result.VCI == 'TSN':
        raise FailedTransaction(result)

    if result.VCI == 'TO':
        # Time limit exceeded.
        raise TimeLimitExceeded

    if result.VCI == 'ABO':
        # Failed transaction.
        raise AbortedTransactionByCardHolder

    if result.VCI == 'U3':
        # Internal authentication error.
        raise U3Exception

    return result


def acknowledge_transaction(token):
    webpay = Webpay(get_webpay_conf())
    result = webpay.getNormalTransaction().acknowledgeTransaction(token)
    return result


