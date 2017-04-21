class Configuration:

    def __init__(self):
        return None;
    
    def setEnvironment(self, environment):
        self.__environment = environment
    
    def getEnvironment(self):
        return self.__environment
    
    def setCommerceCode(self, commercecode):
        self.__commercecode = commercecode
        
    def getCommerceCode(self):
        return self.__commercecode
    
    def setPrivateKey(self, privatekey):
        self.__privatekey = privatekey
    
    def getPrivateKey(self):
        return self.__privatekey
    
    def setPublicCert(self, publiccert):
        self.__publiccert = publiccert
        
    def getPublicCert(self):
        return self.__publiccert
        
    def setWebpayCert(self, webpaycert):
        self.__webpaycert = webpaycert
        
    def getWebPayCert(self):
        return self.__webpaycert
    
    def setStoreCodes(self, storecodes):
        self.__storecodes = storecodes
        
    def getStoreCodes(self):
        return self.__storecodes
    
    def getEnvironmentDefault(self):
        modo = self.__environment
        if (modo == None or modo == ""):
            modo = "INTEGRACION"
        return modo