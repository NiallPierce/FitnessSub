# Generated by Django 4.2.7 on 2025-04-17 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_category_slug_product_is_available_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
