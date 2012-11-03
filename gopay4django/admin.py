from django.contrib import admin
from django.contrib.admin import ModelAdmin
from gopay4django.models import Payment

class PaymentAdmin(ModelAdmin):
    list_display = ("date", "update_date", "name", "state", "last_notify")
    fields = ("name", )

admin.site.register(Payment, PaymentAdmin)
