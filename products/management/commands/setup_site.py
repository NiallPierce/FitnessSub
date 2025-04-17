from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Sets up the default site with the correct domain'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=1)
            site.domain = 'fitness-ecommerce-np92-62c36695dba8.herokuapp.com'
            site.name = 'Fitness Ecommerce'
            site.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated site configuration'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up site: {str(e)}')) 