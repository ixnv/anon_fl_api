from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import OrderCategory


class AccountTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'foo@example.com',
            'username': 'johndoe',
            'password': 'johdoe123'
        }

    def test_can_register(self):
        data = self.user_data
        response = self.client.post('/account/register', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data, {
            'email': data['email'],
            'username': data['username']
        })

    def test_can_login(self):
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])

        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post('/account/login', data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data.keys())


class OrderCategoriesTests(APITestCase):
    def setUp(self):
        self.categories = [{
            'title': 'Foo',
            'parent_id': None
        }, {
            'title': 'Foo child',
            'parent_id': 1
        }, {
            'title': 'Bar',
            'parent_id': None
        }]

    def test_can_list_categories(self):
        OrderCategory.objects.bulk_create(
            [OrderCategory(title=category['title'], parent_id=category['parent_id']) for category in self.categories]
        )

        response = self.client.get('/orders/categories/')
        results = response.data['results']
        self.assertEqual(results[0]['title'], self.categories[0]['title'])
        self.assertEqual(results[0]['subcategories'][0]['id'], 2)
        self.assertEqual(results[0]['subcategories'][0]['title'], self.categories[1]['title'])
        self.assertEqual(results[1]['title'], self.categories[2]['title'])
