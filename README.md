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