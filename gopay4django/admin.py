from django.contrib import admin
from django.contrib.admin import ModelAdmin
from gopay4django.models import Payment

class PaymentAdmin(ModelAdmin):
    list_display = ("date", "update_date", "name", "state", "last_notify", "notify_counter")
    fields = ("name", 'payment_channel', 'currency')
    readonly_fields = ('payment_channel', 'currency')

admin.site.register(Payment, PaymentAdmin)
