from django.core.management.base import BaseCommand, CommandError
from gopay4django.models import Payment
from gopay4django.api import GoPay, GoPayException

class Command(BaseCommand):
    args = ''
    help = 'Check of payments with CREATED state'

    def handle(self, *args, **options):
        try:
            gopay = GoPay()
            for payment in Payment.objects.filter(state="CREATED"):
                gopay.check_payment(payment)
                print "%s: %s" % (payment.name, payment.state)
        except GoPayException:
            CommandError("Error occured during checking")