from django.core.management.base import BaseCommand
from products.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Creates sample subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Basic Plan',
                'description': 'Perfect for beginners starting their fitness journey',
                'price': 9.99,
                'plan_type': 'monthly',
                'features': '''Access to basic workout plans
Basic nutrition guidance
Community forum access
Weekly progress tracking
Email support''',
            },
            {
                'name': 'Pro Plan',
                'description': 'For serious fitness enthusiasts looking to level up',
                'price': 19.99,
                'plan_type': 'monthly',
                'features': '''All Basic Plan features
Customized workout plans
Personalized nutrition plans
Video tutorials
Priority support
Monthly progress review''',
            },
            {
                'name': 'Elite Plan',
                'description': 'The ultimate fitness experience with premium features',
                'price': 29.99,
                'plan_type': 'monthly',
                'features': '''All Pro Plan features
1-on-1 coaching sessions
Advanced analytics
Exclusive content
24/7 support
Custom meal planning
Progress tracking dashboard''',
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created subscription plan: {plan.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Subscription plan already exists: {plan.name}'))
