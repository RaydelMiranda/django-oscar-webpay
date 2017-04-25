Django app for integrating WepPay payment flow into an oscar e-commerce framework
=========================


This django app provides the necessary views and functionality for integrate a WSDL WebPay payment service into adjango-oscar based site.

> **This package has been only tested against the chilean WebPay service.**


> **Important notes about payment flow**
>
> *Operation InitTransaction:* Initializes a transaction in Webpay. In response to the invocation, a 
> Token is generated, which uniquely represents a transaction. It is important to consider that once this method 
> is invoked, the delivered Token has a reduced life span of **5 minutes**, after which the Token 
> is expired and can not be used in a payment.
>
> *Operation getTransactionResult:* Corresponds to the operation after the init Transaction. Allows you to obtain
> the result of the transaction once Webpay has resolved your financial authorization
> 
> *Operation acknowledgeTransaction:* If the invocation is not performed within 30 seconds
> (regardless of the result delivered by the getTransactionResult method), Webpay will reverse the transaction, assuming
> that the trade was unable to report its result, thus preventing cardholder payment.
>
> [Reference](http://www.transbankdevelopers.cl/?m=api "Tbk. Developers")


Settings
--------

In order to use this you must provide some configurations, you can setup the methods you want to use, the methods are:
**NORMAL**, **NORMAL_MALL**, **CAPTURE** or **ONECLICK**.


```python
# Configuration example
WEBPAY_RETURN_IP_ADDRESS = '127.0.0.1'              # Ip address of the host hosting the e-commerce site.
WEBPAY_RETURN_PORT = 8000                           # Port where the server is listening for?

WEBPAY_NORMAL = {


    'ACTIVE_ENVIRON': 'INTEGRATION',                # INTEGRATION, PRODUCTION or CERTIFICATION
                                                    # This values determines which url is used
                                                    # from the 'ENVIRONMENTS' setting.

    'ENVIRONMENTS': {                               # Map the service urls to the active environment value.
        'INTEGRATION': 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
        'CERTIFICATION': 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
        'PRODUCTION': 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl',
    },

    # The following settings are self explanatory.
    'PRIVATE_KEY':  '~/webpay_dev_certs/integracion_normal/597020000541.key',
    'PUBLIC_CERT':  '~/webpay_dev_certs/integracion_normal/597020000541.crt',
    'WEBPAY_CERT':  '~/webpay_dev_certs/integracion_normal/tbk.pem',
    'COMMERCE_CODE': '597020000541'
}

```

Redirecting to **WebpayPaymentDetailsView**
------------------------------------------

Add the following:

```python
 if payment_method.lower() == 'webpay':
        return redirect('webpay-payment')
```

to the `PaymentDetailsView.get` method.


Modifying dependencies
----------------------

If you are experiencing some problems getting this to work properly, try to modify some dependencies according to this:

http://www.transbankdevelopers.cl/?m=api


