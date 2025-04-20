# Fitness E-commerce Website

A full-stack e-commerce platform for fitness products and services, built with Django.

## Features

- User authentication and authorization
- Product catalog and shopping cart
- Secure payment processing with Stripe
- Newsletter subscription
- SEO optimized
- Responsive design

## Live Demo

The application is currently deployed and available at:
https://fitness-ecommerce-np92-62c36695dba8.herokuapp.com/

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

## Deployment to Heroku

### Prerequisites
- Heroku CLI installed
- Git installed
- Heroku account
- Stripe account for payment processing
- PostgreSQL database (provided by Heroku)

### Deployment Steps

1. Login to Heroku:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create fitness-ecommerce-np92
```

3. Add the Heroku remote:
```bash
heroku git:remote -a fitness-ecommerce-np92
```

4. Set up environment variables in Heroku:
```bash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DEBUG=False
heroku config:set STRIPE_PUBLIC_KEY=your_stripe_public_key
heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
heroku config:set STRIPE_WH_SECRET=your_stripe_webhook_secret
heroku config:set EMAIL_HOST_USER=your_email
heroku config:set EMAIL_HOST_PASS=your_email_password
```

5. Add PostgreSQL database:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

6. Push to Heroku:
```bash
git push heroku main
```

7. Run migrations and setup:
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

8. Collect static files:
```bash
heroku run python manage.py collectstatic --noinput
```

### Post-Deployment Verification

After deployment, verify the following:

1. Application is accessible at the Heroku URL
2. Static files are loading correctly
3. Database migrations are applied
4. User authentication is working
5. Product catalog is accessible
6. Shopping cart functionality is working
7. Stripe payment processing is functional
8. Newsletter subscription is working
9. Admin interface is accessible
10. Error pages (404, 500) are properly configured

### Monitoring and Maintenance

1. Check Heroku logs:
```bash
heroku logs --tail
```

2. Scale the application if needed:
```bash
heroku ps:scale web=1
```

3. Backup the database:
```bash
heroku pg:backups:capture
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
- Gunicorn for production server
- WhiteNoise for static file serving

## Testing

Run tests with:
```bash
python manage.py test
```

## Security Considerations

- DEBUG mode is disabled in production
- Secret keys are stored in environment variables
- CSRF protection is enabled
- Secure session handling
- Password hashing
- XSS protection
- SQL injection protection