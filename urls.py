from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url("^success/$", "gopay.views.success", name="gopay_success"),
    url("^failed/$", "gopay.views.failed", name="gopay_failed"),
    url("^notify/$", "gopay.views.notify", name="gopay_notify"),
)
