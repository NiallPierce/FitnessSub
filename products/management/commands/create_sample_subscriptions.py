from django.core.management.base import BaseCommand
from products.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Creates sample subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Basic Plan',
                'description': (
                    'Perfect for beginners '
                    'starting their fitness journey'
                ),
                'price': 9.99,
                'plan_type': 'monthly',
                'features': (
                    'Access to basic workout plans\n'
                    'Basic nutrition guidance\n'
                    'Community forum access\n'
                    'Weekly progress tracking\n'
                    'Email support'
                ),
            },
            {
                'name': 'Pro Plan',
                'description': (
                    'For serious fitness enthusiasts '
                    'looking to level up'
                ),
                'price': 19.99,
                'plan_type': 'monthly',
                'features': (
                    'All Basic Plan features\n'
                    'Customized workout plans\n'
                    'Personalized nutrition plans\n'
                    'Video tutorials\n'
                    'Priority support\n'
                    'Monthly progress review'
                ),
            },
            {
                'name': 'Elite Plan',
                'description': (
                    'The ultimate fitness experience '
                    'with premium features'
                ),
                'price': 29.99,
                'plan_type': 'monthly',
                'features': (
                    'All Pro Plan features\n'
                    '1-on-1 coaching sessions\n'
                    'Advanced analytics\n'
                    'Exclusive content\n'
                    '24/7 support\n'
                    'Custom meal planning\n'
                    'Progress tracking dashboard'
                ),
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created subscription plan: {plan.name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Subscription plan already exists: {plan.name}'
                    )
                )
