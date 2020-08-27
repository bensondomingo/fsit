from django.core.management.base import BaseCommand, CommandError
from tradingapp.models import Stock


class Command(BaseCommand):
    help = 'Create Stock object based on the specified arguments'

    def add_arguments(self, parser) -> None:
        parser.add_argument('name', type=str)
        parser.add_argument('price', type=float)
        parser.add_argument('quantity', type=int)

    def handle(self, *args, **options):
        try:
            data = {
                'name': options.get('name'),
                'price': options.get('price'),
                'quantity': options.get('quantity')
            }
            stock = Stock.objects.create(**data)
        except Exception as e:
            raise CommandError(e)
        self.stdout.write(
            self.style.SUCCESS('Successfully created stock "%s"' % stock.name))
