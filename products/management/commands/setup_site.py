from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Sets up the default site with the correct domain'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=1)
            site.domain = (
                'fitness-ecommerce-np92-62c36695dba8.herokuapp.com'
            )
            site.name = 'Fitness Ecommerce'
            site.save()
            success_msg = 'Successfully updated site configuration'
            self.stdout.write(self.style.SUCCESS(success_msg))
        except Exception as e:
            error_msg = f'Error setting up site: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
