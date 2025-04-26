import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_ecommerce.settings')
django.setup()

from products.models import Product

# Dictionary mapping product names to their correct image paths
image_updates = {
    'Running Shorts': 'images/product_images/shorts.jpeg',
    'Resistance Band Set': 'images/product_images/resistanceband.jpeg',
    'Training Shorts': 'images/product_images/shorts.jpeg',
    'Gym Bag Pro': 'images/product_images/gymbag.jpeg',
    'Performance Hoodie': 'images/product_images/hoodie.jpeg',
    'Training T-Shirt': 'images/product_images/tshirt.jpeg',
    'Performance Training T-Shirt': 'images/product_images/tshirt.jpeg',
    'Gym Bag': 'images/product_images/gymbag.jpeg',
    'Resistance Bands Set': 'images/product_images/resistanceband.jpeg',
    'Energy Gels': 'images/product_images/energygel.jpeg',
    'Skipping Rope': 'images/product_images/skippingrope.jpeg',
    'Protein Bars': 'images/product_images/proteinbar.jpeg',
    'Jump Rope Pro': 'images/product_images/skippingrope.jpeg',
    'Insulated Water Bottle': 'images/product_images/waterbottle.jpeg',
    'Yoga Mat': 'images/product_images/yogamat.jpeg',
    'Yoga Mat Pro': 'images/product_images/yogamat.jpeg',
    'Vegan Protein Powder': 'images/product_images/veganprotein.jpeg',
    'Training Hoodie': 'images/product_images/hoodie.jpeg',
    'Wireless Earbuds': 'images/product_images/earbuds.jpeg',
    'Foam Roller': 'images/product_images/foamroller.jpeg',
    'Massage Gun': 'images/product_images/massagegun.jpeg',
    'Water Bottle Pro': 'images/product_images/waterbottle.jpeg',
    'Energy Gels (10 pack)': 'images/product_images/energygel.jpeg',
    'Protein Bars (12 pack)': 'images/product_images/proteinbar.jpeg',
    'Premium Whey Protein': 'images/product_images/Protein.jpeg',
    'Pull-Up Bar': 'images/product_images/pullup.jpeg',
    'Folding Workout Bench': 'images/product_images/foldingbench.jpeg',
    'Pre-Workout Energy': 'images/product_images/preworkout.jpeg',
    'Adjustable Dumbbell Set': 'images/product_images/dumbell.jpeg',
    'Compression Leggings': 'images/product_images/leggings.jpeg',
    'Fitness Smart Watch': 'images/product_images/watch.jpeg',
    'BCAA Recovery Blend': 'images/product_images/bcaa.jpeg',
}

# Update each product
for product_name, image_path in image_updates.items():
    try:
        product = Product.objects.get(name=product_name)
        product.image = image_path
        product.save()
        print(f"Updated {product_name} image path to {image_path}")
    except Product.DoesNotExist:
        print(f"Product {product_name} not found")
    except Exception as e:
        print(f"Error updating {product_name}: {str(e)}")

print("Image path update complete!") 