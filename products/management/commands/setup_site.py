from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Ensures the default site exists with ID 1'

    def handle(self, *args, **options):
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'fitness-ecommerce-np92-62c36695dba8.herokuapp.com',
                'name': 'Fitness Ecommerce'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created default site'))
        else:
            self.stdout.write(self.style.SUCCESS('Default site already exists')) 