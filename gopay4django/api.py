# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from suds.client import Client
from types import NoneType
from gopay4django.crypt import GoCrypt
from gopay4django.models import Payment

VALID_CURRENCY = ["CZK", "EUR"]
VALID_LANGS = ["CZE"]
FULL_INTGRATION_URL = "https://gate.gopay.cz/gw/pay-full-v2?sessionInfo.targetGoId=%(goId)s&sessionInfo.paymentSessionId=%(sessionId)s&sessionInfo.encryptedSignature=%(encryptedSignature)s"
TEST_FULL_INTGRATION_URL = "https://testgw.gopay.cz/gw/pay-full-v2?sessionInfo.targetGoId=%(goId)s&sessionInfo.paymentSessionId=%(sessionId)s&sessionInfo.encryptedSignature=%(encryptedSignature)s"
TEST_GW = 'https://testgw.gopay.cz/axis/EPaymentServiceV2?wsdl'
GW = 'https://gate.gopay.cz/axis/EPaymentServiceV2?wsdl'
SIGNATURES = {
    # create payment
    "command": ["productName", "totalPrice", "currency", "orderNumber", "failedURL", "successURL", "preAuthorization", "recurrentPayment", "recurrenceDateTo", "recurrenceCycle", "recurrencePeriod", "paymentChannels"],
    # result from create payment
    "command_result": ["productName", "totalPrice", "currency", "orderNumber", "recurrentPayment", "parentPaymentSessionId", "preAuthorization", "result", "sessionState", "sessionSubState", "paymentChannel"],
    # get redirect url
    "redirect": ["paymentSessionId"],
    # get payment status
    "status": ["paymentSessionId"],
    # returned status result
    "status_result": ["productName", "totalPrice", "currency", "orderNumber", "recurrentPayment", "parentPaymentSessionId", "preAuthorization", "result", "sessionState", "sessionSubState", "paymentChannel"],
    # when user comes back to success url
    "identity": ["paymentSessionId", "parentPaymentSessionId", "orderNumber"], # when user is returned back
}

class GoPayException(Exception): pass

class Signature(object):
    def __init__(self, goid=settings.GOPAY_GOID, secret=settings.GOPAY_SECRET_KEY):
        self.goid = goid
        self.secret = secret

    def _prepare_parms(self, parms):
        new_parms = []
        new_parms.append("%d" % self.goid)
        for parm in parms:
            if type(parm) == bool:
                new_parms.append("1" if parm else "0")
            elif type(parm) == NoneType:
                new_parms.append("")
            elif type(parm) == int or type(parm) == long:
                new_parms.append("%d" % parm)
            elif type(parm) == float:
                new_parms.append("%.2f" % parm)
            elif type(parm) == list:
                new_parms.append(",".join(parm))
            elif parm == "false":
                new_parms.append("0")
            elif parm == "true":
                new_parms.append("1")
            elif parm == "null" or parm == "None":
                new_parms.append("")
            else:
                new_parms.append(parm)
        new_parms.append(self.secret)
        return new_parms

    def _create_signature(self, parms, encoded=True):
        long_string = "|".join(parms)
        gocrypt = GoCrypt()
        #print "Long string:".ljust(25), long_string
        #print "Hash:".ljust(25), gocrypt.hash(long_string)
        #print "Encrypted hash:".ljust(25), gocrypt.encrypt_pydes(long_string)
        if encoded:
            signature = gocrypt.encrypt_pydes(long_string)
        else:
            signature = gocrypt.hash(long_string)
        return signature

    def verify_signature(self, signature1, signature2):
        crypt = GoCrypt()
        #print "My ph1", signature1
        #print "Go ph1", signature2
        signature1 = crypt.decrypt_pydes(signature1)
        signature2 = crypt.decrypt_pydes(signature2)
        #print "My ph2", signature1
        #print "Go ph2", signature2
        if signature1 != signature2:
            raise GoPayException("Error: signatures dont't match")
        return True

    def create_status_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["status"]])
        return self._create_signature(parms, encoded=encoded)

    def create_redirect_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["redirect"]])
        return self._create_signature(parms, encoded=encoded)

    def create_command_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["command"]])
        #print parms
        return self._create_signature(parms, encoded=encoded)

    def create_command_result_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["command_result"]])
        return self._create_signature(parms, encoded=encoded)

    def create_status_result_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["status_result"]])
        return self._create_signature(parms, encoded=encoded)

    def create_identity_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["identity"]])
        return self._create_signature(parms, encoded=encoded)

    def create_notification_signature(self, data, encoded=True):
        parms = self._prepare_parms([data[parm] for parm in SIGNATURES["notification"]])
        return self._create_signature(parms, encoded=encoded)


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

    def _settings_check(self):
        pass
        # check combination of payment methods and selected currency

    def _gen_valid_payment_channels(self):
        data = self.get_payment_channels()
        channels_list = []
        for code in data:
            method = data[code]
            channels_list.append(code)
        return channels_list

    def get_client(self):
        return Client(self.gw_url)

    def get_full_integration_url(self, session_id, signature):
        return self.integration_url % {"goId": self.goid, "sessionId": session_id, "encryptedSignature": signature}

    def get_available_payment_channels(self):
        channels = [code for code in self._gen_valid_payment_channels()]
        available_channels = []
        for code in settings.GOPAY_PAYMENT_CHANNELS:
            if code in channels:
                available_channels.append(code)
        if not available_channels:
            raise GoPayException("Error: no available payment channel")
        return available_channels

    def check_payment(self, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        payment_session = {
            "targetGoId": self.goid,
            "paymentSessionId": payment.payment_status.get("paymentSessionId"),
        }

        signature = Signature()
        session_signature = signature.create_status_signature(payment_session)
        payment_session["encryptedSignature"] = session_signature

        client = self.get_client()
        payment_status = client.service.paymentStatus(payment_session)
        if payment_status["result"] != "CALL_COMPLETED":
            raise GoPayException("Error: communication problem (%s)" % payment_status["resultDescription"])
        true_signature = signature.create_status_result_signature(payment_status)
        signature.verify_signature(true_signature, payment_status["encryptedSignature"])

        if payment.payment_command.get("productName") != payment_status["productName"] or \
           payment.payment_command.get("totalPrice") != payment_status["totalPrice"] or \
           payment.payment_command.get("orderNumber") != payment_status["orderNumber"]:
            raise GoPayException("Error: Mishmash productName, totalPrice and orderNumber")

        payment.payment_status = payment_status
        payment.state = payment_status["sessionState"]
        payment.save()

        return True if payment_status["sessionState"] == "PAID" else False

    def get_payment_channels(self):
        client = self.get_client()
        downloaded_methods = client.service.paymentMethodList()
        methods = {}
        for method in downloaded_methods:
            #if method["offline"]: continue
            methods[method["code"]] = {
                "name": method["paymentMethod"],
                "description": method["description"],
                "logo": method["logo"],
                "supportPreauthorization": method["supportPreauthorization"],
                "supportRecurrent": method["supportRecurrent"],
                "supportedCurrency": method["supportedCurrency"],
            }
        return methods

    def create_payment(self,
                          productName,
                          totalPrice,
                          currency,
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
                          lang=settings.GOPAY_LANG,
                          p1=None,
                          p2=None,
                          p3=None,
                          p4=None,
                          name="",
                        ):

        payment = Payment()
        payment.name = name
        payment.p1 = p1
        payment.p2 = p2
        payment.p3 = p3
        payment.p4 = p4
        payment.save()

        if currency not in VALID_CURRENCY:
            raise GoPayException("Error: Wrong currency value")
        if lang not in VALID_LANGS:
            raise GoPayException("Error: Wrong lang value")

        payment_command = {
            "targetGoId": int(self.goid),
            "productName": productName,
            "totalPrice": int(totalPrice*100),
            "currency": currency,
            "orderNumber": payment.id,
            "failedURL": "%s%s" % (settings.GOPAY_DOMAIN, reverse("gopay_failed")),
            "successURL": "%s%s" % (settings.GOPAY_DOMAIN, reverse("gopay_success")),
            "preAuthorization": preAuthorization,
            "recurrentPayment": recurrentPayment,
            "recurrenceDateTo": recurrenceDateTo,
            "recurrenceCycle": recurrenceCycle,
            "recurrencePeriod": recurrencePeriod,
            "paymentChannels": ",".join(self.get_available_payment_channels()),
            "defaultPaymentChannel": defaultPaymentChannel,
            "p1": p1,
            "p2": p2,
            "p3": p3,
            "p4": p4,
            "lang": lang,
            }
        signature = Signature()
        command_signature = signature.create_command_signature(payment_command)
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
        payment_command["encryptedSignature"] = command_signature
        payment_command["customerData"] = client_data

        client = self.get_client()
        payment_status = client.service.createPayment(payment_command)
        if payment_status["result"] != "CALL_COMPLETED":
            raise GoPayException("Error: communication problem (%s)" % payment_status["resultDescription"])
        result_data = payment_command
        result_data.update(payment_status)
        result_signature = signature.create_command_result_signature(result_data)
        signature.verify_signature(result_signature, payment_status["encryptedSignature"])

        payment.state = payment_status["sessionState"]
        payment.payment_status = payment_status
        payment.payment_command = payment_command
        payment.save()

        return self.get_full_integration_url(payment_status["paymentSessionId"], signature.create_redirect_signature(result_data))
