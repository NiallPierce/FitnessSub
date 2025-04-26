from django.core.management.base import BaseCommand
from products.models import SubscriptionPlan
import stripe
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates or updates Stripe products and prices for subscription plans'

    def handle(self, *args, **kwargs):
        if not settings.STRIPE_SECRET_KEY:
            self.stdout.write(self.style.ERROR('Stripe secret key is not configured'))
            return

        stripe.api_key = settings.STRIPE_SECRET_KEY

        for plan in SubscriptionPlan.objects.filter(is_active=True):
            try:
                # First, check if we already have a product and price
                if plan.stripe_product_id and plan.stripe_price_id:
                    try:
                        # Verify the price exists and is recurring
                        price = stripe.Price.retrieve(plan.stripe_price_id)
                        if price.recurring:
                            self.stdout.write(
                                self.style.SUCCESS(f'Price already exists for {plan.name}')
                            )
                            continue
                    except stripe.error.InvalidRequestError:
                        # Price doesn't exist or is invalid, we'll create a new one
                        pass

                # Create or update Stripe product
                product_data = {
                    'name': plan.name,
                    'description': plan.description,
                }

                if plan.stripe_product_id:
                    product = stripe.Product.modify(
                        plan.stripe_product_id,
                        **product_data
                    )
                else:
                    product = stripe.Product.create(**product_data)

                # Create recurring price
                price_data = {
                    'product': product.id,
                    'unit_amount': int(plan.price * 100),  # Convert to cents
                    'currency': 'usd',
                    'recurring': {
                        'interval': 'month',
                    },
                }

                price = stripe.Price.create(**price_data)

                # Update the plan with Stripe IDs
                plan.stripe_product_id = product.id
                plan.stripe_price_id = price.id
                plan.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created Stripe product and price for {plan.name}')
                )
                self.stdout.write(f'Product ID: {product.id}')
                self.stdout.write(f'Price ID: {price.id}')

            except stripe.error.StripeError as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating Stripe product/price for {plan.name}: {str(e)}')
                )
                import traceback
                self.stdout.write(traceback.format_exc())
