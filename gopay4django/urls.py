from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url("^success/$", "gopay4django.views.success", name="gopay_success"),
    url("^failed/$", "gopay4django.views.failed", name="gopay_failed"),
    url("^notify/$", "gopay4django.views.notify", name="gopay_notify"),
)
