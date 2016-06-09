from django.conf.urls import url
from . import views

urlpatterns = [
    url("^success/$", views.success, name="gopay_success"),
    url("^failed/$", views.failed, name="gopay_failed"),
    url("^notify/$", views.notify, name="gopay_notify"),
]
