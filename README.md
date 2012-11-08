Python GoPay API v2.3
=====================

Developed for Fraggo.net s.r.o. <[http://www.fraggo.net/](http://www.fraggo.net/)>

Django app to integrate GoPay into your project.

I implemented just a part of the API:

* paymentStatus
* paymentMethodList
* createPayment

Feel free to add other parts!

Instalation
-----------

    pip install https://github.com/creckx/gopay4django/zipball/master

Configuration
-------------

Add *gopay* into *installed_apps* and set these parameters:

    GOPAY_DOMAIN = "http://<your domain>"
    GOPAY_GOID = <your go id> # should be integer
    GOPAY_FAILED_URL = <success url>
    GOPAY_SUCCESS_URL = <failed url>
    GOPAY_SECRET_KEY = <your secret key>
    GOPAY_TEST_GW = <True or False>
    GOPAY_LANG = <lang>
    GOPAY_DEFAULT_PAYMENT_CHANNEL = "cz_cs_c"
    GOPAY_PAYMENT_CHANNELS = ["cz_gp_u", "cz_gp_w", "cz_rb", "cz_vb", "cz_kb", "cz_cs_c", "cz_mb", "cz_fb", "cz_ge"]

Add this somewhere into your urls.

    url(r'^gopay/', include('gopay4django.urls')),

If you don't know what codes you can use, try:

    python manage.py payment_channels

When user comes back from GoPay to your site, this app handle the request and decide where will be user redirected. If
all goes well, GOPAY_SUCCESS_URL will be used, otherwise GOPAY_FAILED_URL. There is also parametr *payment_uuid* to get
payment data from Payment model.


Usage
-----

    gopay = GoPay()
    url = gopay.create_payment(
        productName = "Jméno produktu",
        totalPrice = 1000,
        currency = "CZK",
        firstName = "Adam,
        lastName = "Štrauch",
        city = "Hradec Králové",
        street = "Ve Stromovce 123",
        postalCode = "50011",
        countryCode = "CZE",
        email = "info@example.com",
        phoneNumber=123456789,
        p1="some data",
        name="Some name, anything what can help you identify payment in administration"
    )

Method create_payment() returns URL to redirect to GoPay payment gateway. After everything is done on gateway, user
comes back to GOPAY_FAILED_URL or GOPAY_SUCCESS_URL.

Signal
------

GoPay sends notifications if something changes (for ex. payment is paid). When it happens, it save new payment status
to database, returns 200 to GoPay gateway and sends signal *payment_changed* which you can catch and do something with it.
Here is some example:

    from gopay4django.signals import payment_changed

    @receiver(payment_changed)
    def payment_changed_callback(sender, **kwargs):
        payment = kwargs.get("payment")
        print "Payment %s changed status to %s" % (payment.uuid, payment.state)

Payment object
--------------

*Payment* model is ordinary model, but has two jsons fields, which you can access as dict.

* Payment.payment_command
* Payment.payment_status

For example:

    payment = Payment.objects.all()[0]
    payment.payment_status.get("sessionState") # returns state of payment
    payment.payment_status.get("p1") # returns optinal paramete p1 (integration manual)
    payment.payment_status.get("p2") # returns optinal paramete p2 (integration manual)