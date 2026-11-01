from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Entry


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


class EntryListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.programming = Category.objects.create(name='Programming')
        self.reading = Category.objects.create(name='Reading')
        self.old = Entry.objects.create(date='2026-10-26', category=self.programming, duration=60)
        self.mid = Entry.objects.create(date='2026-10-28', category=self.reading, duration=30)
        self.new = Entry.objects.create(date='2026-10-31', category=self.programming, duration=45)

    def ids(self, response):
        return [entry['id'] for entry in response.data]

    def test_entries_are_ordered_newest_first(self):
        response = self.client.get('/api/entries/')

        self.assertEqual(self.ids(response), [self.new.id, self.mid.id, self.old.id])

    def test_same_day_entries_are_ordered_by_newest_id(self):
        first = Entry.objects.create(date='2026-11-01', category=self.reading, duration=10)
        second = Entry.objects.create(date='2026-11-01', category=self.reading, duration=20)

        response = self.client.get('/api/entries/')

        self.assertEqual(self.ids(response)[:2], [second.id, first.id])
