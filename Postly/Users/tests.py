from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='pass123')
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, 'reader')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass123')
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, 'admin')
