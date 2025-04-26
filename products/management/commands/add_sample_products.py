from django.core.management.base import BaseCommand
from products.models import Product, Category
from decimal import Decimal
from django.core.files import File
import os
from django.conf import settings
from django.utils.text import slugify


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
                'description': 'High-quality whey protein powder with 24g of protein per serving. Perfect for post-workout recovery and muscle growth.',
                'price': Decimal('39.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'Protein.jpeg'
            },
            {
                'category_slug': 'supplements',
                'name': 'BCAA Recovery Blend',
                'description': 'Essential amino acids blend to support muscle recovery and reduce fatigue. Great for intense training sessions.',
                'price': Decimal('29.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.5'),
                'image_name': 'bcaa.jpeg'
            },
            {
                'category_slug': 'supplements',
                'name': 'Pre-Workout Energy',
                'description': 'Advanced pre-workout formula with caffeine, beta-alanine, and creatine for enhanced performance.',
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
                'description': 'Space-saving adjustable dumbbells with quick-change weight system. Perfect for home workouts.',
                'price': Decimal('199.99'),
                'stock': 20,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'dumbell.jpeg'
            },
            {
                'category_slug': 'equipment',
                'name': 'Pull-Up Bar',
                'description': 'Wall-mounted pull-up bar for upper body strength training. Supports up to 300lbs.',
                'price': Decimal('49.99'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'pullup.jpeg'
            },
            {
                'category_slug': 'equipment',
                'name': 'Folding Workout Bench',
                'description': 'Adjustable folding bench for versatile strength training exercises.',
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
                'description': 'High-performance compression leggings with pocket. Perfect for running and training.',
                'price': Decimal('34.99'),
                'stock': 60,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'leggings.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Training Shorts',
                'description': 'Lightweight and breathable training shorts with built-in liner.',
                'price': Decimal('29.99'),
                'stock': 45,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'shorts.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Performance Hoodie',
                'description': 'Moisture-wicking hoodie with thumb holes and zippered pockets.',
                'price': Decimal('49.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'hoodie.jpeg'
            },
            {
                'category_slug': 'apparel',
                'name': 'Training T-Shirt',
                'description': 'Quick-dry performance t-shirt with anti-odor technology.',
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
                'description': 'Advanced fitness tracking watch with heart rate monitor, GPS, and workout tracking features.',
                'price': Decimal('199.99'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'watch.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Wireless Earbuds',
                'description': 'Sweat-proof wireless earbuds with noise cancellation for focused workouts.',
                'price': Decimal('79.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'earbuds.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Gym Bag',
                'description': 'Spacious gym bag with separate compartments for shoes and wet clothes.',
                'price': Decimal('44.99'),
                'stock': 35,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'gymbag.jpeg'
            },
            {
                'category_slug': 'accessories',
                'name': 'Insulated Water Bottle',
                'description': 'Double-walled insulated water bottle that keeps drinks cold for 24 hours.',
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
                'description': 'Plant-based protein powder with complete amino acid profile.',
                'price': Decimal('34.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'veganprotein.jpeg'
            },
            {
                'category_slug': 'nutrition',
                'name': 'Protein Bars',
                'description': 'High-protein snack bars with natural ingredients and great taste.',
                'price': Decimal('24.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'proteinbar.jpeg'
            },
            {
                'category_slug': 'nutrition',
                'name': 'Energy Gels',
                'description': 'Quick energy gels for endurance training and competitions.',
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
                'description': 'High-density foam roller for muscle recovery and myofascial release.',
                'price': Decimal('29.99'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'foamroller.jpeg'
            },
            {
                'category_slug': 'recovery',
                'name': 'Massage Gun',
                'description': 'Deep tissue percussion massage gun for muscle recovery.',
                'price': Decimal('149.99'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'massagegun.jpeg'
            },
            # Home Gym
            {
                'category_slug': 'home-gym',
                'name': 'Resistance Bands Set',
                'description': 'Set of 5 resistance bands with different tension levels for full-body workouts.',
                'price': Decimal('39.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'resistanceband.jpeg'
            },
            {
                'category_slug': 'home-gym',
                'name': 'Skipping Rope',
                'description': 'Adjustable speed rope with ball bearings for smooth rotation.',
                'price': Decimal('19.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'skippingrope.jpeg'
            },
            {
                'category_slug': 'home-gym',
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with carrying strap and alignment markers.',
                'price': Decimal('29.99'),
                'stock': 35,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'yogamat.jpeg'
            }
        ]

        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)

        # Add products to database
        for product_data in products:
            category_slug = product_data.pop('category_slug')
            image_name = product_data.pop('image_name', None)
            category = Category.objects.get(slug=category_slug)

            # Get or create the product
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={**product_data, 'category': category}
            )

            if not created:
                # Update existing product with new data
                for key, value in product_data.items():
                    setattr(product, key, value)
                product.category = category
                product.save()

            if image_name:
                try:
                    # Source image path (in static directory)
                    source_path = os.path.join(settings.BASE_DIR, 'static', 'product_images', image_name)

                    # Create product_images directory if it doesn't exist
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'images', 'product_images'), exist_ok=True)

                    # Copy the image if it exists
                    if os.path.exists(source_path):
                        # Use the original image name
                        safe_name = image_name
                        # Remove any existing image
                        if product.image:
                            product.image.delete(save=False)
                        with open(source_path, 'rb') as source_file:
                            # Save to the product's image field with the original filename
                            product.image.save(
                                safe_name,
                                File(source_file),
                                save=True
                            )
                            self.stdout.write(
                                self.style.SUCCESS(f'Successfully added image for {product.name}')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Image not found at {source_path}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error adding image for {product.name}: {str(e)}')
                    )

        self.stdout.write(self.style.SUCCESS('Successfully added sample products'))
