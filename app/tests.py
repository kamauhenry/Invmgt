"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from app.models import CustomUser, CustomUserManager, Tenant  , generate_unique_username


# TODO: Configure your database in settings.py and sync before running tests.

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'Home Page', 1, 200)

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact')
        self.assertContains(response, 'Contact', 3, 200)

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about')
        self.assertContains(response, 'About', 3, 200)


class TestCustomUser(TestCase):

    def test_generate_unique_username(self):
        """
        Tests that generate_unique_username returns a unique username.
        """
        username = generate_unique_username()
        self.assertFalse(CustomUser.objects.filter(username=username).exists())

    def test_create_user(self):
        """
        Tests that create_user successfully creates a user with valid data.
        """
        email = "test@example.com"
        password = "password123"

        user = CustomUserManager().create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_tenant(self):
        """
        Tests that create_user can handle a provided tenant object.
        """
        email = "test@example.com"
        password = "password123"
        tenant = Tenant.objects.create(name="Test Tenant")

        user = CustomUserManager().create_user(email, password, tenant=tenant)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.tenant, tenant)
