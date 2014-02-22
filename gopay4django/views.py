import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from gopay4django.api import GoPayException, GoPay, Signature
from gopay4django.crypt import GoCrypt
from gopay4django.models import Payment
from gopay4django.signals import payment_changed

def check(request):
    targetGoId = request.GET.get("targetGoId")
    encryptedSignature = request.GET.get("encryptedSignature")
    orderNumber = request.GET.get("orderNumber")

    try:
        payment = Payment.objects.get(id=int(orderNumber))
    except Payment.DoesNotExist:
        raise GoPayException("Error: payment doesn't exists")

    # check goid and paymentSessionId - should be safe enough
    if targetGoId == settings.GOPAY_GOID or \
       int(request.GET.get("paymentSessionId")) != int(payment.payment_status.get("paymentSessionId")):
        raise GoPayException("Error: GoId or paymentSessionId not match!")

    signature = Signature()
    control_signature = signature.create_identity_signature(request.GET)
    signature.verify_signature(control_signature, encryptedSignature)

    # save new status of payment and return True/False by the state (PAID/not PAID)
    GoPay().check_payment(payment)
    payment_changed.send(sender=request, payment=payment)
    return payment


def success(request):
    try:
        payment = check(request)
    except GoPayException:
        return HttpResponseRedirect("%s?payment_uuid=%s" % (settings.GOPAY_FAILED_URL, payment.uuid))
    return HttpResponseRedirect("%s?payment_uuid=%s" % (settings.GOPAY_SUCCESS_URL, payment.uuid))


def failed(request):
    try:
        payment = check(request)
    except GoPayException:
        pass
    return HttpResponseRedirect("%s?payment_uuid=%s" % (settings.GOPAY_FAILED_URL, payment.uuid))

def notify(request):
    try:
        payment = check(request)
        payment.notify_counter += 1
        payment.last_notify = datetime.datetime.now()
        payment.save()
        response = HttpResponse("OK", content_type="text/plain")
        response.status_code = 200
    except GoPayException:
        response = HttpResponse("ERROR", content_type="text/plain")
        response.status_code = 500
    return response
