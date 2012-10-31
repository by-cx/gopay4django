# -*- coding: utf-8 -*-
from django.conf import settings
from suds.client import Client
from gopay.crypt import GoCrypt

VALID_CURRENCY = ["CZK", "EUR"]
VALID_LANGS = ["CZE"]
VALIED_PAYMENT_CHANNELS = ["cz_gp_w", "cz_gp_u", "cz_rb", "SUPERCASH"]
FULL_INTGRATION_URL = "https://gate.gopay.cz/gw/pay-full-v2?sessionInfo.targetGoId=%(goId)s&sessionInfo.paymentSessionId=%(sessionId)s&sessionInfo.encryptedSignature=%(encryptedSignature)s"
TEST_FULL_INTGRATION_URL = "https://testgw.gopay.cz/gw/pay-full-v2?sessionInfo.targetGoId=%(goId)s&sessionInfo.paymentSessionId=%(sessionId)s&sessionInfo.encryptedSignature=%(encryptedSignature)s"
TEST_GW = 'https://testgw.gopay.cz/axis/EPaymentServiceV2?wsdl'
GW = 'https://gate.gopay.cz/axis/EPaymentServiceV2?wsdl'

class GoPayException(Exception): pass

class GoPay(object):
    def __init__(self, goid=settings.GOPAY_GOID, secret=settings.GOPAY_SECRET_KEY):
        self.goid = goid
        self.secret = secret
        if settings.GOPAY_TEST_GW:
            self.gw_url = TEST_GW
            self.integration_url = TEST_FULL_INTGRATION_URL
        else:
            self.gw_url = GW
            self.integration_url = FULL_INTGRATION_URL

    def get_client(self):
        return Client(self.gw_url)

    def get_full_integration_url(self, session_id, signature):
        return self.integration_url % {"goId": self.goid, "sessionId": session_id, "encryptedSignature": signature}

    def _create_session_signature(self, payment_session_id):
        parms = []
        parms.append("%d" % self.goid)
        parms.append(payment_session_id)
        parms.append(self.secret)
        return self._create_signature(parms)

    def _create_payment_signature(self, data):
        parms = []
        parms.append("%d" % data["targetGoId"])
        parms.append(data["productName"])
        parms.append("%d" % data["totalPrice"])
        parms.append(data["currency"])
        parms.append("%d" % data["orderNumber"])
        parms.append(data["failedURL"])
        parms.append(data["successURL"])
        parms.append("1" if data["preAuthorization"] else "0")
        parms.append("1" if data["recurrentPayment"] else "0")
        parms.append(data["recurrenceDateTo"] if data["recurrenceDateTo"] else "")
        parms.append(data["recurrenceCycle"] if data["recurrenceCycle"] else "")
        parms.append(data["recurrencePeriod"] if data["recurrencePeriod"] else "")
        parms.append(",".join(data["paymentChannels"]))
        parms.append(self.secret)
        return self._create_signature(parms)

    def _create_signature(self, parms):
        long_string = "|".join(parms)
        gocrypt = GoCrypt()
        signature = gocrypt.encrypt_pydes(long_string)
        return signature

    def _verify_signature(self, payment_session, signature):
        gocrypt = GoCrypt()
        my_signature = gocrypt.decrypt_pydes(self._create_session_signature(payment_session))
        go_signature = gocrypt.decrypt_pydes(signature)
        if my_signature != go_signature:
            raise GoPayException("Error: signatures dont't match")
        return True

    def create_payment(self,
                          productName,
                          totalPrice,
                          currency,
                          orderNumber,
                          firstName,
                          lastName,
                          city,
                          street,
                          postalCode,
                          countryCode,
                          email,
                          phoneNumber,
                          preAuthorization=False,
                          recurrentPayment=False,
                          recurrenceDateTo=None,
                          recurrenceCycle=None,
                          recurrencePeriod=None,
                          defaultPaymentChannel=settings.GOPAY_DEFAULT_PAYMENT_CHANNEL,
                          paymentChannels=settings.GOPAY_PAYMENT_CHANNELS,
                          lang=settings.GOPAY_LANG,
                          p1=None,
                          p2=None,
                          p3=None,
                          p4=None,
                        ):

        if currency not in VALID_CURRENCY:
            raise GoPayException("Error: Wrong currency value")
        if lang not in VALID_LANGS:
            raise GoPayException("Error: Wrong lang value")
        if type(totalPrice) not in (float, int):
            raise GoPayException("Error: Wrong price value")
        for channel in paymentChannels:
            if channel not in VALIED_PAYMENT_CHANNELS:
                raise GoPayException("Error: Wrong payment channel value")

        payment_command = {
            "targetGoId": int(self.goid),
            "productName": productName,
            "totalPrice": int(totalPrice*100),
            "currency": currency,
            "orderNumber": orderNumber,
            "failedURL": settings.GOPAY_FAILED_URL,
            "successURL": settings.GOPAY_SUCCESS_URL,
            "preAuthorization": preAuthorization,
            "recurrentPayment": recurrentPayment,
            "recurrenceDateTo": recurrenceDateTo,
            "recurrenceCycle": recurrenceCycle,
            "recurrencePeriod": recurrencePeriod,
            "paymentChannels": paymentChannels,
            "defaultPaymentChannel": defaultPaymentChannel,
            "p1": p1,
            "p2": p2,
            "p3": p3,
            "p4": p4,
            "lang": lang,
            }
        signature = self._create_payment_signature(payment_command)
        client_data = {
            "firstName": firstName,
            "lastName": lastName,
            "city": city,
            "street": street,
            "postalCode": postalCode,
            "countryCode": countryCode,
            "email": email,
            "phoneNumber": phoneNumber,
        }
        payment_command["encryptedSignature"] = signature
        payment_command["customerData"] = client_data

        client = self.get_client()
        payment_status = client.service.createPayment(payment_command)
        self._verify_signature(payment_status["paymentSessionId"], payment_status["encryptedSignature"])
        return self.get_full_integration_url(payment_status["paymentSessionId"], self._create_session_signature(payment_status["paymentSessionId"]))
        #return URL: http://objednavka.1000webu.cz/success/?parentPaymentSessionId=&paymentSessionId=3001297546&encryptedSignature=06214a6de2f7c5c9fab07521fa691ccf8dbad11c41d776d89950bab3a85fc73978155c8ff3ad498def8c01eb0478ef0b&p4=&p3=&targetGoId=8306463847&p2=&p1=&orderNumber=1


def test():
    gopay = GoPay()
    print gopay.create_payment(
        "Test produkt",
        100,
        "CZK",
        1,
        "Adam",
        "Štrauch",
        "Lanškroun",
        "Houští 474",
        "56301",
        "CZE",
        "cx@initd.cz",
        "+420777636388",
    )

