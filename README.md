# Fitness E-commerce Website

A full-stack e-commerce platform for fitness products and services, built with Django.

## Features

- User authentication and authorization
- Product catalog and shopping cart
- Secure payment processing with Stripe
- Newsletter subscription
- SEO optimized
- Responsive design

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WH_SECRET=your_stripe_webhook_secret
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
fitness_ecommerce/
├── accounts/           # User authentication and profiles
├── products/          # Product catalog and management
├── cart/             # Shopping cart functionality
├── checkout/         # Payment processing
├── home/             # Homepage and static pages
└── newsletter/       # Newsletter subscription
```

## Development

This project uses:
- Django 4.2.7
- PostgreSQL
- Stripe for payments
- Bootstrap 5 for frontend
- Django Allauth for authentication

## Deployment

The application is designed to be deployed on a cloud platform (e.g., Heroku, AWS, or DigitalOcean) with PostgreSQL as the database.

## Testing

Run tests with:
```bash
python manage.py test
```