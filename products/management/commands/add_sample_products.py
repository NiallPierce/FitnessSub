from django.core.management.base import BaseCommand
from products.models import Product, Category
from decimal import Decimal
from django.core.files import File
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Adds sample fitness products to the database'

    def handle(self, *args, **options):
        # Create categories if they don't exist
        categories = {
            'supplements': 'Supplements',
            'equipment': 'Equipment',
            'apparel': 'Apparel',
            'accessories': 'Accessories',
            'nutrition': 'Nutrition',
            'recovery': 'Recovery',
            'home-gym': 'Home Gym'
        }

        for slug, name in categories.items():
            Category.objects.get_or_create(
                name=name,
                friendly_name=name,
                slug=slug
            )

        # Sample products data
        products = [
            # Supplements
            {
                'category_slug': 'supplements',
                'name': 'Premium Whey Protein',
                'description': (
                    'High-quality whey protein powder with 24g of protein per '
                    'serving. Perfect for post-workout recovery and muscle '
                    'growth.'
                ),
                'price': Decimal('39.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'Protein.jpeg'
            },
            {
                'category_slug': 'supplements',
                'name': 'BCAA Recovery Blend',
                'description': (
                    'Essential amino acids blend to support '
                    'muscle recovery and reduce fatigue. Great for '
                    'intense training sessions.'
                ),
                'price': Decimal('29.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.5'),
                'image_name': 'bcaa.jpeg'
            },
            {
                'category_slug': 'supplements',
                'name': 'Pre-Workout Energy',
                'description': (
                    'Advanced pre-workout formula with caffeine, '
                    'beta-alanine, and creatine for enhanced '
                    'performance.'
                ),
                'price': Decimal('34.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'preworkout.jpeg'
            },
            # Equipment
            {
                'category_slug': 'equipment',
                'name': 'Adjustable Dumbbell Set',
                'description': (
                    'Space-saving adjustable dumbbells with '
                    'quick-change weight system. Perfect for home '
                    'workouts.'
                ),
                'price': Decimal('199.99'),
                'stock': 20,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'dumbell.jpeg'
            },
            {
                'category_slug': 'equipment',
                'name': 'Pull-Up Bar',
                'description': (
                    'Wall-mounted pull-up bar for upper body '
                    'strength training. Supports up to 300lbs.'
                ),
                'price': Decimal('49.99'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'pullup.jpeg'
            },
            {
                'category_slug': 'equipment',
                'name': 'Folding Workout Bench',
                'description': (
                    'Adjustable folding bench for versatile strength training '
                    'exercises.'
                ),
                'price': Decimal('129.99'),
                'stock': 10,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'foldingbench.jpeg'
            },
            # Apparel
            {
                'category_slug': 'apparel',
                'name': 'Compression Leggings',
                'description': (
                    'High-performance compression leggings with '
                    'pocket. Perfect for running and training.'
                ),
                'price': Decimal('34.99'),
                'stock': 60,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'leggings.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Training Shorts',
                'description': (
                    'Lightweight and breathable training shorts with built-in '
                    'liner.'
                ),
                'price': Decimal('29.99'),
                'stock': 45,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'shorts.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Performance Hoodie',
                'description': (
                    'Moisture-wicking hoodie with thumb holes and zippered '
                    'pockets.'
                ),
                'price': Decimal('49.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'hoodie.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Training T-Shirt',
                'description': (
                    'Quick-dry performance t-shirt with anti-odor technology.'
                ),
                'price': Decimal('24.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'tshirt.jpeg'
            },
            # Accessories
            {
                'category_slug': 'accessories',
                'name': 'Fitness Smart Watch',
                'description': (
                    'Advanced fitness tracking watch with heart rate monitor, '
                    'GPS, and workout tracking features.'
                ),
                'price': Decimal('199.99'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'watch.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Wireless Earbuds',
                'description': (
                    'Sweat-proof wireless earbuds with noise cancellation for '
                    'focused workouts.'
                ),
                'price': Decimal('79.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'earbuds.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Gym Bag',
                'description': (
                    'Spacious gym bag with separate compartments '
                    'for shoes and wet clothes.'
                ),
                'price': Decimal('44.99'),
                'stock': 35,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'gymbag.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Insulated Water Bottle',
                'description': (
                    'Double-walled insulated water bottle that keeps drinks '
                    'cold for 24 hours.'
                ),
                'price': Decimal('29.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'waterbottle.jpeg'
            },
            # Nutrition
            {
                'category_slug': 'nutrition',
                'name': 'Vegan Protein Powder',
                'description': (
                    'Plant-based protein powder with complete amino acid '
                    'profile.'
                ),
                'price': Decimal('34.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'veganprotein.jpeg'
            },
            {
                'category_slug': 'nutrition',
                'name': 'Protein Bars',
                'description': (
                    'High-protein snack bars with natural ingredients and '
                    'great taste.'
                ),
                'price': Decimal('24.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'proteinbar.jpeg'
            },
            {
                'category_slug': 'nutrition',
                'name': 'Energy Gels',
                'description': (
                    'Quick-absorbing energy gels for endurance training and '
                    'competition.'
                ),
                'price': Decimal('19.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.5'),
                'image_name': 'energygel.jpeg'
            },
            # Recovery
            {
                'category_slug': 'recovery',
                'name': 'Foam Roller',
                'description': (
                    'High-density foam roller for muscle recovery and '
                    'self-massage.'
                ),
                'price': Decimal('24.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'foamroller.jpeg'
            },
            {
                'category_slug': 'recovery',
                'name': 'Massage Gun',
                'description': (
                    'Professional-grade percussion massage gun for '
                    'deep tissue massage.'
                ),
                'price': Decimal('149.99'),
                'stock': 20,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'massagegun.jpeg'
            },
            {
                'category_slug': 'recovery',
                'name': 'Compression Sleeves',
                'description': (
                    'Graduated compression sleeves for improved circulation '
                    'and recovery.'
                ),
                'price': Decimal('29.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'compressionsleeves.jpeg'
            },
            # Home Gym
            {
                'category_slug': 'home-gym',
                'name': 'Resistance Bands Set',
                'description': (
                    'Set of 5 resistance bands with different tension levels '
                    'for full-body workouts.'
                ),
                'price': Decimal('39.99'),
                'stock': 35,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'resistancebands.jpeg'
            },
            {
                'category_slug': 'home-gym',
                'name': 'Yoga Mat',
                'description': (
                    'Non-slip, eco-friendly yoga mat with carrying strap.'
                ),
                'price': Decimal('29.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'yogamat.jpeg'
            },
            {
                'category_slug': 'home-gym',
                'name': 'Jump Rope',
                'description': (
                    'Professional speed jump rope with ball bearings for '
                    'smooth rotation.'
                ),
                'price': Decimal('19.99'),
                'stock': 45,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'jumprope.jpeg'
            }
        ]

        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)

        # Add products to database
        for product_data in products:
            try:
                category = Category.objects.get(
                    slug=product_data['category_slug']
                )
                product = Product.objects.create(
                    category=category,
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock'],
                    is_featured=product_data['is_featured'],
                    rating=product_data['rating']
                )

                # Add product image if available
                image_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'product_images',
                    product_data['image_name']
                )
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        product.image.save(
                            product_data['image_name'],
                            File(f),
                            save=True
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully added product: {product.name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error adding product '
                        f'{product_data["name"]}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully added sample products'
            )
        )
