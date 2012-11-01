from django.core.management.base import BaseCommand, CommandError
from gopay.api import GoPay, GoPayException

class Command(BaseCommand):
    args = ''
    help = 'Print available payment channels'

    def handle(self, *args, **options):
        try:
            gopay = GoPay()
            channels = gopay.get_payment_channels()
            for code in channels:
                channel = channels[code]
                self.stdout.write("%s (%s) %s\n" % (channel["name"], code, channel["supportedCurrency"]))
        except GoPayException:
            CommandError("Error occured during geting payment channels")