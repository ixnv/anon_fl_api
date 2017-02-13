import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from rest_framework.authtoken.models import Token

from api import models
from api.models import OrderCategory, Tag, Order, OrderApplication


class Helpers:
    order = {
        'title': 'Title',
        'description': 'Description',
        'price': 10.0,
        'category': 2,
        'tags': [{'id': 1, 'tag': 'Foo'}, {'id': 2, 'tag': 'Bar'}]
    }

    categories = [{
        'title': 'Foo',
        'parent_id': None
    }, {
        'title': 'Foo child',
        'parent_id': 1
    }, {
        'title': 'Bar',
        'parent_id': None
    }]

    tags = [{'tag': 'Tag1', 'created_by_id': 1}, {'tag': 'Tag2', 'created_by_id': 1}]

    user = {'username': 'johndoe1234', 'password': '1234johndoe'}

    @staticmethod
    def create_categories(categories=None):
        if categories is None:
            categories = Helpers.categories
        OrderCategory.objects.bulk_create([OrderCategory(**category) for category in categories])

    @staticmethod
    def create_tags(tags=None):
        if tags is None:
            tags = Helpers.tags
        Tag.objects.bulk_create([Tag(**tag) for tag in tags])

    @staticmethod
    def create_user(username=None, password=None):
        if username is None:
            username = Helpers.user['username']
        if password is None:
            password = Helpers.user['password']

        user = User.objects.create_user(username=username, password=password)
        Token.objects.create(user=user)
        return user

    @staticmethod
    def authorize_client(client, user):
        token = Token.objects.get(user__id=user.pk)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client


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
        Helpers.create_user(self.user_data['username'], self.user_data['password'])

        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post('/account/login', data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data.keys())


class OrderCategoriesTests(APITestCase):
    def test_can_list_categories(self):
        Helpers.create_categories()
        categories = Helpers.categories

        response = self.client.get('/orders/categories/')
        results = response.data['results']
        self.assertEqual(results[0]['title'], categories[0]['title'])
        self.assertEqual(results[0]['subcategories'][0]['id'], 2)
        self.assertEqual(results[0]['subcategories'][0]['title'], categories[1]['title'])
        self.assertEqual(results[1]['title'], categories[2]['title'])


class OrderTests(APITestCase):
    def setUp(self):
        Helpers.create_categories()

        self.user = Helpers.create_user()
        token = Token.objects.get(user__username=Helpers.user['username'])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        Helpers.create_tags()

    def test_can_create_order(self):
        order = json.dumps(Helpers.order)

        response = self.client.post('/orders/', data=order, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderApplicationTests(APITestCase):
    def setUp(self):
        Helpers.create_categories()

        self.user = Helpers.create_user()
        token = Token.objects.get(user__username=Helpers.user['username'])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        Helpers.create_tags()

    def test_can_apply_to_order(self):
        response = self.client.post('/orders/', data=json.dumps(Helpers.order), content_type='application/json')
        order = response.data

        contractor = Helpers.create_user('alice1234', '1234alice')
        self.client = Helpers.authorize_client(self.client, contractor)

        response = self.client.post('/orders/{0}/applications/'.format(order['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 0)

    def test_cannot_apply_to_own_order(self):
        response = self.client.post('/orders/', data=json.dumps(Helpers.order), content_type='application/json')
        order = response.data

        response = self.client.post('/orders/{0}/applications/'.format(order['id']))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEquals(response.data, {'application': 'Cannot apply to own order'})

    def test_cannot_apply_to_order_repeatedly(self):
        response = self.client.post('/orders/', data=json.dumps(Helpers.order), content_type='application/json')
        order = response.data

        user = Helpers.create_user('alice1234', '1234alice')
        self.client = Helpers.authorize_client(self.client, user)

        response = self.client.post('/orders/{0}/applications/'.format(order['id']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 0)

        response = self.client.post('/orders/{0}/applications/'.format(order['id']))
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data, {'application': 'Already applied'})


class OrderApplicationStatusTests(APITestCase):
    def setUp(self):
        Helpers.create_categories()
        Helpers.create_tags()

        self.customer = Helpers.create_user()
        self.client = Helpers.authorize_client(self.client, self.customer)
        self.client.post('/orders/', data=json.dumps(Helpers.order), content_type='application/json')
        self.order = Order.objects.get(id=1)

    def test_customer_can_accept_application(self):
        contractor = Helpers.create_user('alice1234', '1234alice')
        application = OrderApplication.objects.create(applicant_id=contractor.id, order_id=self.order.id)

        response = self.client.put('/orders/{0}/applications/{1}/status/'.format(self.order.id, application.id),
                                   data=json.dumps({'status': models.ApplicationStatus.ACCEPTED.value}),
                                   content_type='application/json')

        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, models.OrderStatus.IN_PROCESS)

    def test_customer_can_decline_application(self):
        contractor = Helpers.create_user('alice1234', '1234alice')
        application = OrderApplication.objects.create(applicant_id=contractor.id, order_id=self.order.id)

        response = self.client.put('/orders/{0}/applications/{1}/status/'.format(self.order.id, application.id),
                                   data=json.dumps({'status': models.ApplicationStatus.DECLINED.value}),
                                   content_type='application/json')

        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, models.OrderStatus.NEW.value)

    def test_customer_do_not_have_permission(self):
        contractor = Helpers.create_user('alice1234', '1234alice')
        application = OrderApplication.objects.create(applicant_id=contractor.id, order_id=self.order.id)

        other_customer = Helpers.create_user('bob123456', '123456bob')
        self.client = Helpers.authorize_client(self.client, other_customer)

        response = self.client.put('/orders/{0}/applications/{1}/status/'.format(self.order.id, application.id),
                                   data=json.dumps({'status': models.ApplicationStatus.DECLINED.value}),
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
