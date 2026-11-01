from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category


class CategoryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_returns_categories_sorted_by_name(self):
        Category.objects.create(name='Reading', is_default=True)
        Category.objects.create(name='Exercise')

        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([c['name'] for c in response.data], ['Exercise', 'Reading'])

    def test_create_category(self):
        response = self.client.post('/api/categories/', {'name': 'Gym'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Gym')
        self.assertFalse(response.data['is_default'])

    def test_create_rejects_exact_duplicate_name(self):
        Category.objects.create(name='Gym')

        response = self.client.post('/api/categories/', {'name': 'Gym'}, format='json')

        self.assertEqual(response.status_code, 400)
