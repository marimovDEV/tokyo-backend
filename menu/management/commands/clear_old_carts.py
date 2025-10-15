from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from menu.models import Cart


class Command(BaseCommand):
    help = 'Clear old carts from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Delete carts older than this many days (default: 1)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all carts'
        )

    def handle(self, *args, **options):
        if options['all']:
            count = Cart.objects.all().count()
            Cart.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted all {count} carts')
            )
        else:
            days = options['days']
            cutoff_date = timezone.now() - timedelta(days=days)
            old_carts = Cart.objects.filter(updated_at__lt=cutoff_date)
            count = old_carts.count()
            old_carts.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {count} carts older than {days} days'
                )
            )



