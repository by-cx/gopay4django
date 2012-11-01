from django.contrib import admin
from django.contrib.admin import ModelAdmin
from gopay.models import Payment

class PaymentAdmin(ModelAdmin):
    list_display = ("date", "update_date", "name", "state")
    fields = ("name", )

admin.site.register(Payment, PaymentAdmin)
