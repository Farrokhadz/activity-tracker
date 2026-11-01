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

        response = self.client.get('/api/entries/?date=2026-11-01')

        self.assertEqual(self.ids(response), [second.id, first.id])

    def test_filter_by_single_date(self):
        response = self.client.get('/api/entries/?date=2026-10-28')

        self.assertEqual(self.ids(response), [self.mid.id])

    def test_filter_by_date_range_is_inclusive(self):
        response = self.client.get('/api/entries/?from=2026-10-28&to=2026-10-31')

        self.assertEqual(self.ids(response), [self.new.id, self.mid.id])

    def test_filter_by_category(self):
        response = self.client.get(f'/api/entries/?category={self.programming.id}')

        self.assertEqual(self.ids(response), [self.new.id, self.old.id])

    def test_filters_can_be_combined(self):
        response = self.client.get(
            f'/api/entries/?from=2026-10-27&category={self.programming.id}'
        )

        self.assertEqual(self.ids(response), [self.new.id])

    def test_malformed_date_returns_400(self):
        response = self.client.get('/api/entries/?from=yesterday')

        self.assertEqual(response.status_code, 400)
        self.assertIn('from', response.data)

    def test_impossible_date_returns_400(self):
        response = self.client.get('/api/entries/?date=2026-02-31')

        self.assertEqual(response.status_code, 400)

    def test_non_numeric_category_returns_400(self):
        response = self.client.get('/api/entries/?category=abc')

        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.data)


class EntryDetailApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.programming = Category.objects.create(name='Programming')
        self.reading = Category.objects.create(name='Reading')
        self.entry = Entry.objects.create(
            date='2026-10-31', category=self.programming, duration=45, note='API work'
        )
        self.url = f'/api/entries/{self.entry.id}/'

    def test_get_single_entry(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['duration'], 45)
        self.assertEqual(response.data['note'], 'API work')

    def test_patch_updates_only_the_given_fields(self):
        response = self.client.patch(self.url, {'duration': 50}, format='json')

        self.assertEqual(response.status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.duration, 50)
        self.assertEqual(self.entry.note, 'API work')
        self.assertEqual(self.entry.category_id, self.programming.id)

    def test_patch_can_change_category(self):
        response = self.client.patch(self.url, {'category': self.reading.id}, format='json')

        self.assertEqual(response.status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.category_id, self.reading.id)

    def test_patch_with_invalid_data_returns_400(self):
        response = self.client.patch(self.url, {'date': 'not-a-date'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('date', response.data)

    def test_delete_removes_the_entry(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Entry.objects.filter(pk=self.entry.id).exists())

    def test_missing_entry_returns_404_for_every_method(self):
        missing = '/api/entries/99999/'

        self.assertEqual(self.client.get(missing).status_code, 404)
        self.assertEqual(self.client.patch(missing, {'duration': 5}, format='json').status_code, 404)
        self.assertEqual(self.client.delete(missing).status_code, 404)


class ValidationRulesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Programming')

    def post_entry(self, duration):
        return self.client.post(
            '/api/entries/',
            {'date': '2026-11-01', 'category': self.category.id, 'duration': duration},
            format='json',
        )

    def test_duration_of_zero_is_rejected(self):
        response = self.post_entry(0)

        self.assertEqual(response.status_code, 400)
        self.assertIn('duration', response.data)

    def test_duration_above_one_day_is_rejected(self):
        response = self.post_entry(1441)

        self.assertEqual(response.status_code, 400)
        self.assertIn('duration', response.data)

    def test_duration_boundaries_are_accepted(self):
        self.assertEqual(self.post_entry(1).status_code, 201)
        self.assertEqual(self.post_entry(1440).status_code, 201)

    def test_patch_cannot_set_an_invalid_duration(self):
        entry = Entry.objects.create(date='2026-11-01', category=self.category, duration=30)

        response = self.client.patch(f'/api/entries/{entry.id}/', {'duration': 0}, format='json')

        self.assertEqual(response.status_code, 400)
