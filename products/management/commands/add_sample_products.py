from django.core.management.base import BaseCommand
from products.models import Product, Category
from decimal import Decimal
from django.core.files import File
from pathlib import Path
import os

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
                'category': 'supplements',
                'name': 'Vegan Protein Powder',
                'description': 'Plant-based protein powder with complete amino acid profile. Perfect for vegan athletes.',
                'price': Decimal('44.99'),
                'stock': 25,
                'is_featured': False,
                'rating': Decimal('4.7')
            },

            # Equipment
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
                'category': 'equipment',
                'name': 'Yoga Mat Pro',
                'description': 'Premium non-slip yoga mat with extra cushioning. Perfect for yoga, pilates, and floor exercises.',
                'price': Decimal('49.99'),
                'stock': 40,
                'is_featured': False,
                'rating': Decimal('4.6')
            },
            {
                'category': 'equipment',
                'name': 'Resistance Band Set',
                'description': 'Set of 5 resistance bands with different tension levels. Includes door anchor and exercise guide.',
                'price': Decimal('29.99'),
                'stock': 60,
                'is_featured': True,
                'rating': Decimal('4.5')
            },
            {
                'category': 'equipment',
                'name': 'Jump Rope Pro',
                'description': 'Professional-grade jump rope with ball bearings and adjustable length. Perfect for cardio workouts.',
                'price': Decimal('19.99'),
                'stock': 45,
                'is_featured': False,
                'rating': Decimal('4.4')
            },

            # Apparel
            {
                'category': 'apparel',
                'name': 'Performance Training T-Shirt',
                'description': 'Moisture-wicking training t-shirt with breathable fabric. Available in multiple colors.',
                'price': Decimal('24.99'),
                'stock': 100,
                'is_featured': False,
                'rating': Decimal('4.4')
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
            },
            {
                'category': 'apparel',
                'name': 'Running Shorts',
                'description': 'Lightweight running shorts with built-in liner and zippered pocket. Quick-dry material.',
                'price': Decimal('29.99'),
                'stock': 75,
                'is_featured': True,
                'rating': Decimal('4.6')
            },
            {
                'category': 'apparel',
                'name': 'Training Hoodie',
                'description': 'Warm-up hoodie with thumb holes and kangaroo pocket. Perfect for pre and post-workout.',
                'price': Decimal('44.99'),
                'stock': 50,
                'is_featured': False,
                'rating': Decimal('4.7')
            },

            # Accessories
            {
                'category': 'accessories',
                'name': 'Fitness Tracker Watch',
                'description': 'Smart fitness tracker with heart rate monitor, step counter, and sleep tracking.',
                'price': Decimal('79.99'),
                'stock': 25,
                'is_featured': True,
                'rating': Decimal('4.7')
            },
            {
                'category': 'accessories',
                'name': 'Gym Bag Pro',
                'description': 'Spacious gym bag with separate compartments for shoes and wet items. Water-resistant material.',
                'price': Decimal('44.99'),
                'stock': 35,
                'is_featured': False,
                'rating': Decimal('4.5')
            },
            {
                'category': 'accessories',
                'name': 'Wireless Earbuds',
                'description': 'Sweat-proof wireless earbuds with 8-hour battery life. Perfect for workouts.',
                'price': Decimal('59.99'),
                'stock': 30,
                'is_featured': True,
                'rating': Decimal('4.8')
            },
            {
                'category': 'accessories',
                'name': 'Water Bottle Pro',
                'description': 'Insulated water bottle that keeps drinks cold for 24 hours. BPA-free and leak-proof.',
                'price': Decimal('24.99'),
                'stock': 80,
                'is_featured': False,
                'rating': Decimal('4.6')
            },

            # Nutrition
            {
                'category': 'nutrition',
                'name': 'Protein Bars (12 pack)',
                'description': 'High-protein snack bars with natural ingredients. Perfect for on-the-go nutrition.',
                'price': Decimal('29.99'),
                'stock': 40,
                'is_featured': True,
                'rating': Decimal('4.5')
            },
            {
                'category': 'nutrition',
                'name': 'Energy Gels (10 pack)',
                'description': 'Quick energy gels for endurance training. Various flavors available.',
                'price': Decimal('19.99'),
                'stock': 60,
                'is_featured': False,
                'rating': Decimal('4.3')
            },

            # Recovery
            {
                'category': 'recovery',
                'name': 'Foam Roller',
                'description': 'High-density foam roller for muscle recovery and flexibility training.',
                'price': Decimal('24.99'),
                'stock': 35,
                'is_featured': True,
                'rating': Decimal('4.7')
            },
            {
                'category': 'recovery',
                'name': 'Massage Gun',
                'description': 'Professional-grade percussion massage gun with multiple attachments.',
                'price': Decimal('149.99'),
                'stock': 15,
                'is_featured': True,
                'rating': Decimal('4.8')
            },

            # Home Gym
            {
                'category': 'home-gym',
                'name': 'Folding Workout Bench',
                'description': 'Adjustable workout bench that folds for easy storage. Supports up to 300kg.',
                'price': Decimal('129.99'),
                'stock': 10,
                'is_featured': True,
                'rating': Decimal('4.6')
            },
            {
                'category': 'home-gym',
                'name': 'Pull-Up Bar',
                'description': 'Doorway-mounted pull-up bar with multiple grip positions.',
                'price': Decimal('39.99'),
                'stock': 25,
                'is_featured': False,
                'rating': Decimal('4.5')
            }
        ]

        # Add products to database
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        images_dir = os.path.join(base_dir, 'static', 'images')

        for product_data in products:
            category = Category.objects.get(slug=product_data['category'])
            image_name = product_data.pop('image_name', None)
            
            product, created = Product.objects.get_or_create(
                category=category,
                name=product_data['name'],
                defaults=product_data
            )

            if created and image_name:
                try:
                    image_path = os.path.join(images_dir, image_name)
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            product.image.save(image_name, File(f), save=True)
                            self.stdout.write(self.style.SUCCESS(f'Added image for {product.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Image not found at {image_path}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to add image for {product.name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully added sample products')) 