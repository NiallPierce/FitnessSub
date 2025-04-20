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
                'category': 'supplements',
                'name': 'Premium Whey Protein',
                'description': 'High-quality whey protein powder with 24g of protein per serving. Perfect for post-workout recovery and muscle growth.',
                'price': Decimal('39.99'),
                'stock': 50,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'Protein.jpeg'
            },
            {
                'category': 'supplements',
                'name': 'BCAA Recovery Blend',
                'description': 'Essential amino acids blend to support muscle recovery and reduce fatigue. Great for intense training sessions.',
                'price': Decimal('29.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.5'),
                'image_name': 'bcaa.jpeg'
            },
            {
                'category': 'supplements',
                'name': 'Pre-Workout Energy',
                'description': 'Advanced pre-workout formula with caffeine, beta-alanine, and creatine for enhanced performance.',
                'price': Decimal('34.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.6'),
                'image_name': 'preworkout.jpeg'
            },
            {
                'category': 'equipment',
                'name': 'Adjustable Dumbbell Set',
                'description': 'Space-saving adjustable dumbbells with quick-change weight system. Perfect for home workouts.',
                'price': Decimal('199.99'),
                'stock': 20,
                'is_featured': True,
                'rating': Decimal('4.7'),
                'image_name': 'dumbell.jpeg'
            },
            {
                'category': 'apparel',
                'name': 'Compression Leggings',
                'description': 'High-performance compression leggings with pocket. Perfect for running and training.',
                'price': Decimal('34.99'),
                'stock': 60,
                'is_featured': True,
                'rating': Decimal('4.9'),
                'image_name': 'leggings.jpeg'
            }
        ]

        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)

        # Add products to database
        for product_data in products:
            category = Category.objects.get(slug=product_data['category'])
            image_name = product_data.pop('image_name', None)
            
            # Get or create the product
            product, created = Product.objects.get_or_create(
                category=category,
                name=product_data['name'],
                defaults=product_data
            )

            if image_name:
                try:
                    # Source image path (in static directory)
                    source_path = os.path.join(settings.BASE_DIR, 'static', 'images', image_name)
                    
                    # Destination path (in media directory)
                    dest_path = os.path.join(settings.MEDIA_ROOT, 'product_images', image_name)
                    
                    # Create product_images directory if it doesn't exist
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copy the image if it exists
                    if os.path.exists(source_path):
                        with open(source_path, 'rb') as source_file:
                            # Save to the product's image field
                            product.image.save(
                                os.path.basename(image_name),
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