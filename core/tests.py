from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Item

class ItemAPITests(APITestCase):
    def setUp(self):
        # Create a regular user
        self.user = User.objects.create_user('alice', 'a@a.com', 'pass1234')
        self.client = APIClient()

        # Create some items (only `name` is required)
        Item.objects.create(name="Alpha")
        Item.objects.create(name="Bravo")

    def test_list_items(self):
        """Any user (even unauthenticated) can list items."""
        resp = self.client.get(reverse('item-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # we should see exactly the two items we created
        names = [item['name'] for item in resp.data['results']]
        self.assertCountEqual(names, ["Alpha", "Bravo"])

    def test_unauthorized_create(self):
        """Unauthenticated users cannot create."""
        resp = self.client.post(reverse('item-list'),
                                {'name':'Charlie'},
                                format='json')
        self.assertIn(resp.status_code,
                      (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.assertEqual(Item.objects.count(), 2)

    def test_authorized_create(self):
        """Logged-in users can create."""
        self.client.login(username='alice', password='pass1234')
        resp = self.client.post(reverse('item-list'),
                                {'name':'Charlie'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 3)
        self.assertEqual(Item.objects.last().name, 'Charlie')
