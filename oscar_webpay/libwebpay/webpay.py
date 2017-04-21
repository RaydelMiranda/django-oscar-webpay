from configuration import Configuration
from webpay_normal import WebpayNormal
from webpay_mall_normal import WebpayMallNormal
"""
from webpay_nullify import WebpayNullify
"""
from webpay_complete import WebpayComplete
"""
from webpay_capture import WebpayCapture
"""
from webpay_oneclick import WebpayOneClick


class Webpay:
    
        def __init__(self, params):
            self.__configuration = params
            return None

        def getNormalTransaction(self):
            webpayNormal = WebpayNormal(self.__configuration)
            return webpayNormal

        def getMallNormalTransaction(self):
            webpayMallNormal = WebpayMallNormal(self.__configuration)
            return webpayMallNormal
        
        """
        def getNullifyTransaction(self):
            webpayNullify = WebpayNullify(self.__configuration)
            return webpayNullify
        """
        
        def getCompleteTransaction(self):
            webpayComplete = WebpayComplete(self.__configuration)
            return webpayComplete
        
        """
        def getCaptureTransaction(self):
            webpayCapture = WebpayCapture(self.__configuration)
            return webpayCapture
        """
        
        def getOneClickTransaction(self):
            webpayOneClick = WebpayOneClick(self.__configuration)
            return webpayOneClick
        