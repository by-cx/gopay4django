from django.dispatch import Signal

payment_changed = Signal(providing_args=["payment"])