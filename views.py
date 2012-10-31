from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from gopay.api import GoPayException, GoPay, Signature
from gopay.crypt import GoCrypt
from gopay.models import Payment


def success(request):
    targetGoId = request.GET.get("targetGoId")
    encryptedSignature = request.GET.get("encryptedSignature")
    orderNumber = request.GET.get("orderNumber")

    try:
        payment = Payment.objects.get(id=int(orderNumber))
    except Payment.DoesNotExist:
        return HttpResponseRedirect("%s?payment_id=%s" % (settings.GOPAY_FAILED_URL, payment.id))

    # check goid and paymentSessionId - should be safe enough
    if targetGoId == settings.GOPAY_GOID or \
       int(request.GET.get("paymentSessionId")) != int(payment.payment_status.get("paymentSessionId")):
        return HttpResponseRedirect("%s?payment_id=%s" % (settings.GOPAY_FAILED_URL, payment.id))

    signature = Signature()
    control_signature = signature.create_identity_signature(request.GET)
    signature.verify_signature(control_signature, encryptedSignature)

    # save new status of payment
    gopay = GoPay()
    gopay.check_payment(payment.id)

    return HttpResponseRedirect("%s?payment_uuid=%s" % (settings.GOPAY_SUCCESS_URL, payment.uuid))


def failed(request):
    targetGoId = request.GET.get("targetGoId")
    encryptedSignature = request.GET.get("encryptedSignature")
    p1 = request.GET.get("p1")
    p2 = request.GET.get("p2")
    p3 = request.GET.get("p3")
    p4 = request.GET.get("p4")
    orderNumber = request.GET.get("orderNumber")
    if targetGoId == settings.GOPAY_GOID:
        return HttpResponseRedirect(settings.GOPAY_FATAL_ERROR_URL)

    payment = Payment.objects.get(id=int(orderNumber))
    if not payment:
        return HttpResponseRedirect(settings.GOPAY_FATAL_ERROR_URL)

    signature = Signature()
    control_signature = signature.create_identity_signature(request.GET)
    signature.verify_signature(control_signature, encryptedSignature)

    # save new status of payment
    gopay = GoPay()
    gopay.check_payment(payment.id)

    return HttpResponseRedirect("%s?payment_uuid=%s" % (settings.GOPAY_FAILED_URL, payment.uuid))