Django app for integrating WepPay payment flow into an oscar e-commerce framework
=========================


This django app provides the necessary views and functionality for integrate a WSDL WebPay payment service into adjango-oscar based site.


Settings
--------

In order to use this you must provide some configurations, you can setup the methods you want to use, the methods are:
**NORMAL**, **NORMAL_MALL**, **CAPTURE** or **ONECLICK**.


```
python
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

