from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps

class Command(BaseCommand):
    help = 'Creates profile objects for all existing users'

    def handle(self, *args, **options):
        User = get_user_model()
        Profile = apps.get_model('accounts', 'Profile')
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} profiles')) 