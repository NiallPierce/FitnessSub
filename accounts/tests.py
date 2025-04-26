from django.test import TestCase, Client
from django.contrib.auth.models import User


class AccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = '/accounts/signup/'
        self.login_url = '/accounts/login/'
        self.logout_url = '/accounts/logout/'

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # User registration data
        self.user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newuserpass123',
            'password2': 'newuserpass123',
        }

    def tearDown(self):
        # Clean up all users except the test user
        User.objects.exclude(username='testuser').delete()

    def test_user_registration(self):
        """Test user registration functionality"""
        response = self.client.post(
            self.register_url,
            self.user_data
        )
        self.assertEqual(
            response.status_code,
            302
        )  # Should redirect after successful registration
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data"""
        # Test with mismatched passwords
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'wrongpass123'
        response = self.client.post(
            self.register_url,
            invalid_data
        )
        self.assertEqual(
            response.status_code,
            200
        )  # Should stay on the same page
        self.assertFalse(
            User.objects.filter(username='newuser').exists()
        )

    def test_user_login(self):
        """Test user login functionality"""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'testpass123'
            }
        )
        self.assertEqual(
            response.status_code,
            302
        )  # Should redirect after successful login
        self.assertTrue(
            '_auth_user_id' in self.client.session
        )

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'wrongpass'
            }
        )
        self.assertEqual(
            response.status_code,
            200
        )  # Should stay on the same page
        self.assertFalse(
            '_auth_user_id' in self.client.session
        )

    def test_user_logout(self):
        """Test user logout functionality"""
        # First login
        self.client.login(
            username='testuser',
            password='testpass123'
        )
        # Then logout
        response = self.client.get(self.logout_url)
        self.assertEqual(
            response.status_code,
            302
        )  # Should redirect after logout
        self.assertFalse(
            '_auth_user_id' in self.client.session
        )

    def test_password_validation(self):
        """Test password validation rules"""
        # Test with too short password
        invalid_data = self.user_data.copy()
        invalid_data['password1'] = 'short'
        invalid_data['password2'] = 'short'
        response = self.client.post(
            self.register_url,
            invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='newuser').exists()
        )

        # Test with numeric-only password
        invalid_data['password1'] = '12345678'
        invalid_data['password2'] = '12345678'
        response = self.client.post(
            self.register_url,
            invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='newuser').exists()
        )

    def test_email_validation(self):
        """Test email validation"""
        # Test with invalid email format
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(
            self.register_url,
            invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='newuser').exists()
        )

    def test_unique_email_validation(self):
        """Test that email must be unique"""
        # First registration
        response = self.client.post(
            self.register_url,
            self.user_data
        )
        self.assertEqual(
            response.status_code,
            302
        )  # Should redirect after successful registration
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

        # Second registration with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'anotheruser'
        response = self.client.post(
            self.register_url,
            duplicate_data
        )
        self.assertEqual(
            response.status_code,
            200
        )  # Should show form with errors
        self.assertFalse(
            User.objects.filter(username='anotheruser').exists()
        )

        # Check for error message in form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('email', form.errors)
        self.assertIn(
            'already in use',
            str(form.errors['email'])
        )
