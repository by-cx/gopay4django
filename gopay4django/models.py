import json
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Payment(models.Model):
    uuid = models.CharField(_("UUID"), max_length=64, blank=True, null=True)
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    update_date = models.DateTimeField(_("Last update date"), auto_now=True)
    state = models.CharField(_("State"), max_length=32, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=256, blank=True, null=True, help_text=_("Identification string. Use what ever you want."))
    p1 = models.CharField(_("P1"), max_length=256, blank=True, null=True)
    p2 = models.CharField(_("P2"), max_length=256, blank=True, null=True)
    p3 = models.CharField(_("P3"), max_length=256, blank=True, null=True)
    p4 = models.CharField(_("P4"), max_length=256, blank=True, null=True)
    last_notify = models.DateTimeField(_("Last notify"), blank=True, null=True, default=None)
    notify_counter = models.IntegerField(_("Notify counter"), default=0)
    _payment_command = models.TextField(_("Payment command"), blank=True, null=True)
    _payment_status = models.TextField(_("Payment status"), blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.uuid:
            self.uuid = "%s" % uuid.uuid4()
        return super(Payment, self).save(force_insert, force_update, using)

    def _set_payment_command(self, value):
        self._payment_command = json.dumps(dict(value))
    def _get_payment_command(self):
        return json.loads(self._payment_command)
    payment_command = property(_get_payment_command, _set_payment_command)

    def _set_payment_status(self, value):
        self._payment_status = json.dumps(dict(value))
    def _get_payment_status(self):
        return json.loads(self._payment_status)
    payment_status = property(_get_payment_status, _set_payment_status)

