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
                'category_slug': 'accessories',
                'name': 'Fitness Smart Watch',
                'description': 'Advanced fitness tracking watch with heart rate monitor, GPS, and workout tracking features.',
                'price': Decimal('199.99'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.8'),
                'image_name': 'watch.jpeg'
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
                        # Generate a consistent filename based on the product name
                        safe_name = slugify(product.name) + os.path.splitext(image_name)[1]
                        # Remove any existing image
                        if product.image:
                            product.image.delete(save=False)
                        with open(source_path, 'rb') as source_file:
                            # Save to the product's image field with the consistent filename
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