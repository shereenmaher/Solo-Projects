
from django.core.management.base import BaseCommand
from ...models import Shipment


class Command(BaseCommand):
    help = "Refresh tracking data for all shipments"

    def handle(self, *args, **options):
        shipments = Shipment.objects.all()

        for shipment in shipments:
            refreshed = Shipment.objects.refresh_shipment(shipment)

            if refreshed:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {shipment.number}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not update {shipment.number}"
                    )
                )
