# Fitness E-commerce Platform

A comprehensive e-commerce platform specializing in fitness products and services, built with Django. This platform offers a complete shopping experience with user management, product catalog, secure payments, and community features.

## 🌟 Key Features

### User Management
- User registration and authentication
- Profile management
- Password reset functionality
- User subscription management

### Product Management
- Comprehensive product catalog
- Category-based navigation
- Product search and filtering
- Product reviews and ratings
- Stock management
- Featured products section

### Shopping Experience
- Shopping cart functionality
- Secure checkout process
- Order history and tracking
- Order status updates
- Multiple payment options
- Order confirmation emails

### Payment Processing
- Secure payment processing via Stripe
- Support for multiple payment methods
- Webhook handling for payment events
- Subscription management
- Payment receipt generation
- Payment method management
- Subscription cancellation and updates

### Community Features
- Product reviews and ratings
- User profiles
- Newsletter subscription
- Email notifications

### Admin Features
- Comprehensive admin dashboard
- Product management
- Order management
- User management
- Analytics and reporting

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Stripe account
- AWS S3 account (for media storage)

### Installation
1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run development server: `python manage.py runserver`

### Environment Variables
Create a `.env` file with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WH_SECRET=your-stripe-webhook-secret
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🚀 Live Demo

The application is currently deployed and available at:
https://fitness-ecommerce-np92-62c36695dba8.herokuapp.com/

## 🛠️ Technical Stack

### Backend
- Django 4.2.7
- PostgreSQL
- Django Allauth
- Django Crispy Forms
- Gunicorn
- WhiteNoise

### Frontend
- Bootstrap 5
- JavaScript
- jQuery
- HTML5/CSS3

### Services
- Stripe (Payments)
- AWS S3 (Media Storage)
- Heroku (Hosting)
- Neon (Database)
- Gmail SMTP (Email)

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL
- Git
- Virtual Environment

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/NiallPierce/FitnessSub.git
cd FitnessSub
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following variables:
```env
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
DEVELOPMENT=True

# Database Settings
DATABASE_URL=your_database_url

# Stripe Settings
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WH_SECRET=your_stripe_webhook_secret

# Email Settings
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASS=your_email_password

# AWS Settings
USE_AWS=True
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Django Allauth Settings
SITE_ID=1
```

5. Database setup:
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## 🌐 Deployment

### Heroku Deployment

1. Install Heroku CLI and login:
```bash
heroku login -i
```

2. Create and configure Heroku app:
```bash
heroku create fitness-ecommerce-np92
heroku git:remote -a fitness-ecommerce-np92
```

3. Set up environment variables:
```bash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DEBUG=False
heroku config:set STRIPE_PUBLIC_KEY=your_stripe_public_key
heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
heroku config:set STRIPE_WH_SECRET=your_stripe_webhook_secret
heroku config:set EMAIL_HOST_USER=your_email
heroku config:set EMAIL_HOST_PASS=your_email_password
heroku config:set USE_AWS=True
heroku config:set AWS_STORAGE_BUCKET_NAME=your_bucket_name
heroku config:set AWS_S3_REGION_NAME=your_region
heroku config:set AWS_ACCESS_KEY_ID=your_access_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret_key
```

4. Deploy the application:
```bash
git push heroku main
```

5. Run migrations and collect static files:
```bash
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
```

## 📁 Project Structure

```
fitness_ecommerce/
├── accounts/           # User authentication and profiles
├── products/          # Product catalog and management
├── cart/             # Shopping cart functionality
├── checkout/         # Payment processing
├── home/             # Homepage and static pages
├── newsletter/       # Newsletter subscription
├── profiles/         # User profile management
├── community/        # Community features
├── static/           # Static files
│   ├── css/         # CSS files
│   ├── js/          # JavaScript files
│   └── product_images/ # Product images
└── templates/        # HTML templates
```

## 🔒 Security Features

- CSRF protection
- XSS protection
- SQL injection protection
- Secure password hashing
- Environment variable management
- SSL/TLS enforcement
- Secure session handling
- Rate limiting
- Input validation

## 🧪 Testing

The project includes comprehensive test coverage for various components. Below is a summary of the test suites and their status:

### Django Test Suites

| App | Test Case | Description | Status |
|-----|-----------|-------------|--------|
| accounts | test_form_validation_feedback | Tests form validation for login and registration | ✅ |
| accounts | test_success_messages | Tests success messages for login and registration | ✅ |
| checkout | test_checkout_view | Tests checkout process with items in cart | ✅ |
| checkout | test_stripe_payment_intent_creation | Tests Stripe payment intent creation | ✅ |
| products | test_product_detail_view | Tests product detail page rendering | ✅ |
| products | test_product_search | Tests product search functionality | ✅ |
| profiles | test_order_history_view | Tests order history view functionality | ✅ |
| profiles | test_profile_creation | Tests automatic profile creation | ✅ |
| profiles | test_profile_update | Tests profile update functionality | ✅ |
| profiles | test_profile_picture_upload | Tests profile picture upload and resizing | ✅ |
| profiles | test_profile_view_authentication | Tests profile view authentication | ✅ |
| profiles | test_profile_data_validation | Tests profile data validation | ✅ |
| profiles | test_newsletter_subscription_toggle | Tests newsletter subscription toggle | ✅ |

### JavaScript Test Suites

| File | Test Case | Description | Status |
|------|-----------|-------------|--------|
| checkout.js | test_form_validation | Tests checkout form validation | ✅ |
| checkout.js | test_payment_processing | Tests Stripe payment processing | ✅ |
| community.js | test_post_creation | Tests post creation and validation | ✅ |
| community.js | test_like_functionality | Tests post and comment likes | ✅ |
| community.js | test_comment_system | Tests comment creation and replies | ✅ |
| community.js | test_challenge_participation | Tests challenge joining and updates | ✅ |

### Running Tests

#### Django Tests
```bash
# Run all Django tests
python manage.py test --keepdb

# Run specific app tests
python manage.py test <app_name>.tests --keepdb

# Run specific test case
python manage.py test <app_name>.tests.<TestClass>.<test_method> --keepdb
```

#### JavaScript Tests
```bash
# Run all JavaScript tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test file
npx jest static/js/checkout.test.js
```

### Test Coverage

The tests cover:
- User authentication and registration
- Product search and filtering
- Shopping cart functionality
- Checkout process
- Payment processing
- Form validation
- Success/error message handling
- Community features (posts, comments, likes)
- Challenge participation

### Linting
The project uses ESLint for JavaScript code quality. Run the linter with:
```bash
# Check for issues
npm run lint

# Fix issues automatically
npm run lint:fix
```

## 📈 Monitoring and Maintenance

### Logging
```bash
heroku logs --tail
```

### Database Backups
```bash
heroku pg:backups:capture
```

### Scaling
```bash
heroku ps:scale web=1
```

## 📋 User Stories Mapping

### 1. User Authentication & Profiles

#### User Registration
**User Story:**
As a new user
I want to register for an account
So that I can access personalized features

**Implementation:**
- Django Allauth integration
- Custom user model
- Email verification
- Profile creation signals

**Acceptance Criteria:**
- [x] User can register with email/password
- [x] Email verification system
- [x] Profile creation on registration
- [x] Welcome email sent
- [x] Error handling for existing users

#### User Login
**User Story:**
As a registered user
I want to log in to my account
So that I can access my personal information and make purchases

**Implementation:**
- Django authentication system
- Session management
- Remember me functionality

**Acceptance Criteria:**
- [x] Secure login form
- [x] Password reset functionality
- [x] Session management
- [x] Remember me feature

### 2. Product Management

#### Product Browsing
**User Story:**
As a customer
I want to browse products by category
So that I can find what I'm looking for

**Implementation:**
- Category-based navigation
- Product search
- Filtering system
- Product detail pages

**Acceptance Criteria:**
- [x] Category navigation
- [x] Search functionality
- [x] Filter options
- [x] Product details
- [x] Image gallery

#### Product Reviews
**User Story:**
As a customer
I want to review products I've purchased
So that I can share my experience with others

**Implementation:**
- Review submission system
- Rating system
- Review moderation
- Review display

**Acceptance Criteria:**
- [x] Review form
- [x] Star rating system
- [x] Moderation tools
- [x] Review display
- [x] User verification

### 3. Shopping Experience

#### Shopping Cart
**User Story:**
As a customer
I want to add products to my cart
So that I can purchase multiple items

**Implementation:**
- Session-based cart
- AJAX updates
- Quantity management
- Price calculations

**Acceptance Criteria:**
- [x] Add/remove items
- [x] Update quantities
- [x] Calculate totals
- [x] Save cart between sessions
- [x] Clear cart after purchase

#### Checkout Process
**User Story:**
As a customer
I want to complete my purchase
So that I can receive my products

**Implementation:**
- Stripe payment integration
- Order processing
- Confirmation emails
- Order tracking
- Order status updates

**Acceptance Criteria:**
- [x] Secure checkout
- [x] Multiple payment options
- [x] Order confirmation
- [x] Email notifications
- [x] Order tracking
- [x] Order status updates

### 4. Admin Features

#### Product Management
**User Story:**
As an administrator
I want to manage products
So that I can keep the catalog up to date

**Implementation:**
- Admin dashboard
- Product CRUD operations
- Image management
- Stock tracking

**Acceptance Criteria:**
- [x] Add/edit products
- [x] Manage categories
- [x] Upload images
- [x] Track stock
- [x] Bulk operations

#### Order Management
**User Story:**
As an administrator
I want to manage orders
So that I can process customer purchases

**Implementation:**
- Order dashboard
- Status updates
- Order search
- Customer communication

**Acceptance Criteria:**
- [x] View all orders
- [x] Update order status
- [x] Search orders
- [x] View order details
- [x] Contact customers

### 5. Community Features

#### Newsletter
**User Story:**
As a user
I want to subscribe to newsletters
So that I can receive updates and promotions

**Implementation:**
- Newsletter subscription
- Email templates
- Unsubscribe option
- Email sending system

**Acceptance Criteria:**
- [x] Subscription form
- [x] Email confirmation
- [x] Unsubscribe option
- [x] Newsletter templates
- [x] Email sending

## 💼 E-commerce Business Model

### Target Market
- Fitness enthusiasts
- Athletes
- Health-conscious consumers
- Gym owners and trainers

### Revenue Streams
1. Product Sales
   - Fitness equipment
   - Supplements
   - Apparel
   - Accessories

2. Subscription Services
   - Monthly fitness plans
   - Premium content access
   - Exclusive product discounts

3. Value Propositions
   - High-quality fitness products
   - Expert-curated content
   - Community support
   - Personalized recommendations

### Marketing Strategy
- Social media presence (Facebook, Instagram)
- Email marketing through newsletter
- SEO optimization
- Community engagement
- Influencer partnerships

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Documentation
- Stripe Documentation
- Heroku Documentation

## 📊 Project Management

### Agile Development with GitHub
This project uses GitHub's built-in project management tools for Agile development:

#### GitHub Projects
- Project board: [Fitness E-commerce Project Board](https://github.com/NiallPierce/FitnessSub/projects)
- Kanban-style workflow with columns:
  - Backlog
  - To Do
  - In Progress
  - Review
  - Done

#### Issue Tracking
- User stories and tasks tracked as GitHub Issues
- Labels for categorization:
  - Feature
  - Bug
  - Enhancement
  - Documentation
  - Testing

#### Milestones
- Project phases tracked as GitHub Milestones
- Sprint planning and tracking
- Release management

#### Pull Requests
- Code review process
- Continuous Integration checks
- Automated testing

### Development Workflow
1. Create issues for user stories and tasks
2. Assign issues to project board columns
3. Create feature branches for development
4. Submit pull requests for review
5. Deploy to production after approval

## 🎨 UX Design Documentation

### Design Principles

1. **Accessibility**
   - ARIA labels for interactive elements
   - Alt text for all images
   - Breadcrumb navigation
   - High contrast color scheme
   - Responsive text sizing
   - Keyboard navigation support

2. **Mobile Responsiveness**
   - Media queries for different screen sizes
   - Responsive grid system
   - Touch-friendly interface elements
   - Collapsible navigation for smaller screens
   - Optimized images with srcset

3. **User Interface**
   - Clean, uncluttered interface
   - Consistent design language
   - Clear visual feedback for actions
   - Streamlined navigation
   - Visual hierarchy for content

### Implemented Features

1. **Navigation & Information Architecture**
   - Hierarchical category structure
   - Persistent search functionality
   - Clear call-to-action buttons
   - Breadcrumb navigation
   - Mobile-friendly navigation menu

2. **Product Discovery**
   - Visual product cards with key information
   - Category-based filtering
   - Search functionality
   - Featured products section
   - Product detail pages

3. **Shopping Experience**
   - One-page checkout process
   - Persistent cart icon with item count
   - Clear pricing and shipping information
   - Multiple payment options
   - Order confirmation system

4. **User Account Management**
   - Registration and login system
   - Profile management
   - Order history
   - Subscription management
   - Password reset functionality

### Technical Implementation

1. **CSS Architecture**
   - CSS variables for consistent styling
   - Responsive design using media queries
   - Custom components for reusability
   - Animation and transition effects
   - Mobile-first approach

2. **Accessibility Features**
   - Semantic HTML structure
   - ARIA attributes for screen readers
   - Keyboard navigation support
   - Focus management
   - Error handling and feedback
   - Modal accessibility
   - Table responsiveness
   - Responsive images with srcset

3. **Performance Optimization**
   - Responsive images with srcset
   - Optimized CSS and JavaScript
   - Efficient DOM manipulation
   - Browser compatibility
   - Responsive tables for mobile views